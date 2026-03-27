#!/usr/bin/env python3

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
DOCS_DIR = ROOT / "docs"
PAPERS_DIR = DOCS_DIR / "papers"
DAILY_DIR = DOCS_DIR / "daily"

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ANGLE_LINK_RE = re.compile(r"<(https?://[^>]+)>")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

TAG_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("MoE", ("moe", "expert", "grouped routing")),
    ("Diffusion", ("diffusion", "flow matching", "flow-matching")),
    ("Long Context", ("long-context", "100m tokens", "memory", "context")),
    ("Multimodal", ("multimodal", "vision-language", "image", "speech")),
    ("Dataset", ("dataset", "benchmark", "bench")),
    ("Agents", ("agent", "coding agent")),
    ("Speech", ("tts", "speech", "voice")),
    ("3D Vision", ("3d", "gaussian", "splatting", "render")),
    ("Robotics", ("driving", "trajectory", "robot", "action")),
    ("Theory", ("schrödinger", "foundations", "bridge")),
]


@dataclass
class SummaryNote:
    slug: str
    title: str
    arxiv_id: str
    source_url: str
    authors: str
    summary: str
    insight: str
    source_path: Path
    tags: list[str]


@dataclass
class DigestEntry:
    title: str
    arxiv_id: str
    note_name: str
    summary: str
    insight: str
    preferred: bool


@dataclass
class DailyDigest:
    title: str
    date_text: str
    highlights: list[str]
    entries: list[DigestEntry]
    source_path: Path


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return value or "paper"


def strip_ticks(text: str) -> str:
    return text.strip().strip("`")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def infer_tags(*texts: str) -> list[str]:
    haystack = " ".join(texts).lower()
    tags = [tag for tag, needles in TAG_RULES if any(needle in haystack for needle in needles)]
    return tags or ["General"]


def render_inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = MD_LINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1), quote=False)}</a>',
        escaped,
    )
    escaped = ANGLE_LINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(1), quote=True)}">{html.escape(m.group(1), quote=False)}</a>',
        escaped,
    )
    escaped = INLINE_CODE_RE.sub(lambda m: f"<code>{html.escape(m.group(1), quote=False)}</code>", escaped)
    return escaped


def render_paragraphs(text: str) -> str:
    blocks = [compact(block) for block in text.split("\n\n") if compact(block)]
    return "\n".join(f"<p>{render_inline(block)}</p>" for block in blocks)


def render_tag_pills(tags: list[str], *, button: bool = False) -> str:
    pill_tag = "button" if button else "span"
    extra = ' type="button"' if button else ""
    return "".join(
        f'<{pill_tag} class="topic-pill" data-tag="{html.escape(tag, quote=True)}"{extra}>{html.escape(tag)}</{pill_tag}>'
        for tag in tags
    )


def parse_summary(path: Path) -> SummaryNote:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].removeprefix("# ").strip()
    meta: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in lines[1:]:
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
            continue
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            meta[key.strip()] = value.strip()

    summary = compact("\n".join(sections.get("摘要总结", [])))
    insight = compact("\n".join(sections.get("核心 Insight", [])))
    return SummaryNote(
        slug=slugify(title),
        title=title,
        arxiv_id=strip_ticks(meta.get("arXiv", "")),
        source_url=meta.get("Source URL", "").strip("<>"),
        authors=meta.get("Authors", "unknown"),
        summary=summary,
        insight=insight,
        source_path=path,
        tags=infer_tags(title, summary, insight),
    )


def parse_digest(path: Path, note_map: dict[str, SummaryNote]) -> DailyDigest:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].removeprefix("# ").strip()
    match = DATE_RE.search(title)
    date_text = match.group(1) if match else path.stem.removeprefix("daily_papers_")

    preferred_tokens: set[str] = set()
    highlights: list[str] = []
    entries: list[DigestEntry] = []
    current_title: str | None = None
    current_data: dict[str, str] = {}

    def is_preferred(text: str) -> bool:
        lowered = text.lower()
        return any(token.lower() in lowered for token in preferred_tokens)

    def flush() -> None:
        nonlocal current_title, current_data
        if not current_title:
            return
        note_name = Path(current_data.get("本地 note", "").strip("`")).name
        note = note_map.get(note_name)
        entries.append(
            DigestEntry(
                title=current_title,
                arxiv_id=strip_ticks(current_data.get("arXiv", "")),
                note_name=note_name,
                summary=current_data.get("摘要总结", ""),
                insight=current_data.get("核心 insight", ""),
                preferred=is_preferred(current_title) or (note is not None and is_preferred(note.title)),
            )
        )
        current_title = None
        current_data = {}

    for line in lines[1:]:
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            if heading == "今日偏好相关":
                current_title = None
                current_data = {}
                continue
            current_title = heading
            current_data = {}
            continue
        if line.startswith("- ") and current_title is None:
            bullet = line[2:].strip()
            highlights.append(bullet)
            preferred_tokens.update(INLINE_CODE_RE.findall(bullet))
            continue
        if line.startswith("- ") and current_title:
            content = line[2:]
            if "：" in content:
                key, value = content.split("：", 1)
                current_data[key.strip()] = value.strip()
            elif ":" in content:
                key, value = content.split(":", 1)
                current_data[key.strip()] = value.strip()

    flush()
    return DailyDigest(title=title, date_text=date_text, highlights=highlights, entries=entries, source_path=path)


def page_shell(title: str, body: str, description: str, stylesheet: str, script: str) -> str:
    return f"""<!doctype html>
<html lang="zh-Hans">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description, quote=True)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{html.escape(stylesheet, quote=True)}">
  </head>
  <body>
    {body}
    <script src="{html.escape(script, quote=True)}"></script>
  </body>
</html>
"""


def build_card(entry: DigestEntry, note: SummaryNote | None, *, href_prefix: str = "") -> str:
    link = f"{href_prefix}papers/{note.slug}.html" if note else "#"
    tags = note.tags if note else infer_tags(entry.title, entry.summary, entry.insight)
    tag_data = ",".join(tags).lower()
    card_classes = "paper-card is-preferred" if entry.preferred else "paper-card"
    badge = '<span class="badge badge-accent">Preferred</span>' if entry.preferred else ""
    return f"""
    <article class="{card_classes}" data-title="{html.escape(entry.title.lower(), quote=True)}" data-tags="{html.escape(tag_data, quote=True)}" data-preferred="{str(entry.preferred).lower()}">
      <div class="card-top">
        <span class="paper-id">arXiv {html.escape(entry.arxiv_id)}</span>
        {badge}
      </div>
      <div class="topic-row">{render_tag_pills(tags)}</div>
      <h2><a href="{html.escape(link, quote=True)}">{html.escape(entry.title)}</a></h2>
      <p class="summary">{render_inline(entry.summary)}</p>
      <p class="insight"><strong>Insight.</strong> {render_inline(entry.insight)}</p>
      <a class="card-link" href="{html.escape(link, quote=True)}">Read note</a>
    </article>
    """


def build_index(latest_digest: DailyDigest, notes: list[SummaryNote], note_map: dict[str, SummaryNote], digests: list[DailyDigest]) -> str:
    highlight_items = "\n".join(f"<li>{render_inline(item)}</li>" for item in latest_digest.highlights)
    cards = "".join(build_card(entry, note_map.get(entry.note_name), href_prefix="./") for entry in latest_digest.entries)
    current_tags = sorted({tag for entry in latest_digest.entries for tag in (note_map.get(entry.note_name).tags if note_map.get(entry.note_name) else [])})
    filter_bar = render_tag_pills(current_tags, button=True)
    library = "\n".join(
        f'<li><a href="./papers/{note.slug}.html">{html.escape(note.title)}</a><span>arXiv {html.escape(note.arxiv_id)}</span></li>'
        for note in sorted(notes, key=lambda item: item.title.lower())
    )
    archive = "\n".join(
        f'<li><a href="./daily/{digest.date_text}.html">{html.escape(digest.date_text)}</a><span>{len(digest.entries)} papers</span></li>'
        for digest in sorted(digests, key=lambda item: item.date_text, reverse=True)
    )
    preferred_titles = [entry.title for entry in latest_digest.entries if entry.preferred][:4]
    preferred_list = "".join(f"<li>{html.escape(title)}</li>" for title in preferred_titles)
    body = f"""
    <div class="page-shell">
      <header class="hero">
        <div class="hero-grid">
          <section class="hero-copy-block">
            <p class="eyebrow">Paper Reading Log</p>
            <h1>Daily papers, packaged for reading instead of skimming.</h1>
            <p class="hero-copy">A lightweight GitHub Pages front-end for Hugging Face Daily Papers notes. The homepage emphasizes your current reading taste: MoE, long-context memory, and diffusion-adjacent generative work.</p>
            <div class="hero-meta">
              <span>Latest digest: {html.escape(latest_digest.date_text)}</span>
              <span>{len(latest_digest.entries)} papers</span>
              <span>{sum(1 for entry in latest_digest.entries if entry.preferred)} preferred picks</span>
            </div>
          </section>
          <aside class="hero-panel">
            <p class="eyebrow">Editor Focus</p>
            <h2>What this front page is optimizing for</h2>
            <ul class="hero-list">
              {preferred_list}
            </ul>
          </aside>
        </div>
      </header>

      <main class="layout">
        <section class="main-column">
          <section class="digest-ribbon">
            <div class="section-head">
              <div>
                <p class="eyebrow">Latest Digest</p>
                <h2>{html.escape(latest_digest.title)}</h2>
              </div>
              <a class="ghost-link" href="./daily/{html.escape(latest_digest.date_text, quote=True)}.html">Open digest view</a>
            </div>
            <ul class="highlight-list">{highlight_items}</ul>
          </section>

          <section class="filter-panel">
            <div class="filter-head">
              <div>
                <p class="eyebrow">Filter Deck</p>
                <h3>Search by title or topic</h3>
              </div>
            </div>
            <div class="search-row">
              <input id="paper-search" class="search-input" type="search" placeholder="Search title, topic, or idea">
              <button id="preferred-toggle" class="filter-toggle" type="button">Preferred only</button>
            </div>
            <div class="topic-filter-row">{filter_bar}</div>
          </section>

          <div id="paper-grid" class="card-grid">
            {cards}
          </div>
          <p id="empty-state" class="empty-state" hidden>No papers match the current filter.</p>
        </section>

        <aside class="side-column">
          <section class="side-panel">
            <p class="eyebrow">Archive</p>
            <h3>Daily digests</h3>
            <ul class="library-list">{archive}</ul>
          </section>
          <section class="side-panel">
            <p class="eyebrow">Library</p>
            <h3>All notes</h3>
            <ul class="library-list">{library}</ul>
          </section>
        </aside>
      </main>
    </div>
    """
    return page_shell("Paper Reading", body, "Daily paper reading digest and note library", "./styles.css", "./app.js")


def build_note_page(note: SummaryNote) -> str:
    body = f"""
    <div class="page-shell note-shell">
      <nav class="top-nav">
        <a href="../index.html">Home</a>
      </nav>
      <article class="note-page">
        <div class="note-hero">
          <div class="note-main">
            <p class="eyebrow">Paper Note</p>
            <h1>{html.escape(note.title)}</h1>
            <div class="topic-row topic-row-large">{render_tag_pills(note.tags)}</div>
          </div>
          <aside class="note-meta-rail">
            <div class="meta-grid">
              <div><span>arXiv</span><strong>{html.escape(note.arxiv_id)}</strong></div>
              <div><span>Source</span><strong><a href="{html.escape(note.source_url, quote=True)}">Open paper</a></strong></div>
              <div><span>Local note</span><strong>{html.escape(str(note.source_path.relative_to(ROOT)))}</strong></div>
            </div>
          </aside>
        </div>
        <section class="content-block content-block-emphasis">
          <h2>摘要总结</h2>
          {render_paragraphs(note.summary)}
        </section>
        <section class="content-block">
          <h2>核心 Insight</h2>
          {render_paragraphs(note.insight)}
        </section>
      </article>
    </div>
    """
    return page_shell(note.title, body, note.summary[:180], "../styles.css", "../app.js")


def build_digest_page(digest: DailyDigest, note_map: dict[str, SummaryNote]) -> str:
    cards = "".join(build_card(entry, note_map.get(entry.note_name), href_prefix="../") for entry in digest.entries)
    highlights = "\n".join(f"<li>{render_inline(item)}</li>" for item in digest.highlights)
    body = f"""
    <div class="page-shell">
      <nav class="top-nav">
        <a href="../index.html">Home</a>
      </nav>
      <section class="digest-head">
        <p class="eyebrow">Digest View</p>
        <h1>{html.escape(digest.title)}</h1>
        <ul class="highlight-list">{highlights}</ul>
      </section>
      <section class="card-grid">{cards}</section>
    </div>
    """
    return page_shell(digest.title, body, f"{digest.title} reading digest", "../styles.css", "../app.js")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    notes = [parse_summary(path) for path in sorted(KNOWLEDGE_DIR.glob("summary_*.md"))]
    note_map = {note.source_path.name: note for note in notes}
    digests = [parse_digest(path, note_map) for path in sorted(KNOWLEDGE_DIR.glob("daily_papers_*.md"))]
    if not notes or not digests:
        raise SystemExit("knowledge/ 缺少 daily digest 或 summary 笔记，无法生成页面。")

    latest_digest = sorted(digests, key=lambda item: item.date_text)[-1]
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    write_text(DOCS_DIR / "index.html", build_index(latest_digest, notes, note_map, digests))
    for note in notes:
        write_text(PAPERS_DIR / f"{note.slug}.html", build_note_page(note))
    for digest in digests:
        write_text(DAILY_DIR / f"{digest.date_text}.html", build_digest_page(digest, note_map))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
