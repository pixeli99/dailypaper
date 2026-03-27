#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

HF_DAILY_PAPERS_API = "https://huggingface.co/api/daily_papers"
HF_PAPER_API = "https://huggingface.co/api/papers/{paper_id}"
HF_PAPER_MD = "https://huggingface.co/papers/{paper_id}.md"
DEFAULT_HELPER = Path("/Users/pixeli/.codex/skills/read-arxiv-paper/scripts/fetch_arxiv_source.py")
DEFAULT_SITE_BUILDER = Path("./scripts/build_github_pages.py")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
COMMAND_RE = re.compile(r"\\[a-zA-Z@]+(\[[^\]]*\])?(\{[^{}]*\})?")
BRACE_RE = re.compile(r"[{}]")
WHITESPACE_RE = re.compile(r"\s+")
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")


@dataclass
class PaperSummary:
    paper_id: str
    title: str
    authors: list[str]
    hf_url: str
    source_url: str
    summary: str
    insight: str
    local_note: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Hugging Face Daily Papers and write local markdown summaries.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date in YYYY-MM-DD format.")
    parser.add_argument("--limit", type=int, default=20, help="Max number of papers to fetch.")
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        default=Path("./knowledge"),
        help="Directory where markdown notes will be written.",
    )
    parser.add_argument(
        "--helper-path",
        type=Path,
        default=DEFAULT_HELPER,
        help="Path to fetch_arxiv_source.py from the read-arxiv-paper skill.",
    )
    parser.add_argument(
        "--build-site",
        action="store_true",
        help="Rebuild the GitHub Pages site after summaries are written.",
    )
    parser.add_argument(
        "--site-builder",
        type=Path,
        default=DEFAULT_SITE_BUILDER,
        help="Path to the GitHub Pages builder script.",
    )
    return parser.parse_args()


def get_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "paper-reading-automation/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def get_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "paper-reading-automation/1.0",
            "Accept": "text/markdown",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def load_prepare_source(helper_path: Path):
    spec = importlib.util.spec_from_file_location("fetch_arxiv_source", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load arXiv helper from {helper_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "prepare_source"):
        raise RuntimeError(f"Helper at {helper_path} does not expose prepare_source")
    return module.prepare_source


def fetch_daily_papers(target_date: str, limit: int) -> list[dict[str, Any]]:
    url = f"{HF_DAILY_PAPERS_API}?p=0&limit={limit}&date={target_date}&sort=publishedAt"
    data = get_json(url)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("papers", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    raise RuntimeError(f"Unexpected Daily Papers payload shape from {url}")


def paper_id_from_item(item: dict[str, Any]) -> str:
    candidates = [
        item.get("paper", {}).get("id") if isinstance(item.get("paper"), dict) else None,
        item.get("paper", {}).get("arxivId") if isinstance(item.get("paper"), dict) else None,
        item.get("arxivId"),
        item.get("id"),
        item.get("slug"),
    ]
    for value in candidates:
        if isinstance(value, str) and re.match(r"^\d{4}\.\d{4,5}(?:v\d+)?$", value):
            return value
    raise RuntimeError(f"Could not determine arXiv id from Daily Papers item: {item}")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "paper"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    index = 2
    while True:
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if "%" not in line:
            lines.append(line)
            continue
        cleaned = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(cleaned)
    return "\n".join(lines)


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.replace("\n", " ")).strip()


def latex_to_text(text: str) -> str:
    cleaned = strip_comments(text)
    replacements = {
        "~": " ",
        "``": '"',
        "''": '"',
    }
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)
    cleaned = re.sub(r"\\[a-zA-Z@]+\*?\s*", " ", cleaned)
    cleaned = re.sub(r"\$[^$]*\$", " ", cleaned)
    cleaned = COMMAND_RE.sub(" ", cleaned)
    cleaned = BRACE_RE.sub(" ", cleaned)
    return normalize_whitespace(cleaned)


def resolve_include(base: Path, root: Path, name: str) -> Path | None:
    rel = Path(name.strip())
    if rel.is_absolute() or ".." in rel.parts:
        return None
    probes = [rel] if rel.suffix else [rel.with_suffix(".tex"), rel.with_suffix(".ltx")]
    for probe in probes:
        for candidate in (base / probe, root / probe):
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()
    return None


def collect_tex_text(entrypoint: Path, root: Path, visited: set[Path] | None = None) -> str:
    visited = visited or set()
    entrypoint = entrypoint.resolve()
    if entrypoint in visited or not entrypoint.exists():
        return ""
    visited.add(entrypoint)
    raw = entrypoint.read_text(encoding="utf-8", errors="ignore")

    def replace_include(match: re.Match[str]) -> str:
        names = [name.strip() for name in match.group(1).split(",")]
        chunks: list[str] = []
        for name in names:
            included = resolve_include(entrypoint.parent, root, name)
            if included is not None:
                chunks.append(collect_tex_text(included, root, visited))
        return "\n".join(chunk for chunk in chunks if chunk)

    return INPUT_RE.sub(replace_include, raw)


def extract_abstract(text: str) -> str:
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, flags=re.S)
    if not match:
        return ""
    return latex_to_text(match.group(1))


def extract_section_snippets(text: str) -> dict[str, str]:
    positions = list(SECTION_RE.finditer(text))
    snippets: dict[str, str] = {}
    for index, match in enumerate(positions):
        title = latex_to_text(match.group(2)).lower()
        start = match.end()
        end = positions[index + 1].start() if index + 1 < len(positions) else len(text)
        snippets[title] = latex_to_text(text[start:end])
    return snippets


def choose_sentences(text: str, limit: int = 2) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", normalize_whitespace(text))
    chosen = [sentence.strip() for sentence in sentences if sentence.strip()]
    return " ".join(chosen[:limit]).strip()


def choose_insight(abstract: str, sections: dict[str, str], fallback_markdown: str) -> str:
    preferred_titles = [
        "conclusion",
        "discussion",
        "overview",
        "introduction",
        "method",
    ]
    for title in preferred_titles:
        for section_title, content in sections.items():
            if title in section_title and content:
                sentence = choose_sentences(content, limit=2)
                if sentence:
                    return sentence
    markdown_sentences = choose_sentences(fallback_markdown, limit=2)
    if markdown_sentences:
        return markdown_sentences
    return choose_sentences(abstract, limit=2)


def format_authors(metadata: dict[str, Any]) -> list[str]:
    authors = metadata.get("authors") or []
    names: list[str] = []
    for author in authors:
        if isinstance(author, dict):
            name = author.get("name") or author.get("fullName")
            if isinstance(name, str) and name.strip():
                names.append(name.strip())
        elif isinstance(author, str) and author.strip():
            names.append(author.strip())
    return names


def write_summary_file(
    knowledge_dir: Path,
    paper_id: str,
    title: str,
    authors: list[str],
    source_url: str,
    archive_path: str,
    extract_dir: str,
    entrypoint: str | None,
    summary: str,
    insight: str,
) -> Path:
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    note_path = unique_path(knowledge_dir / f"summary_{slugify(title)}.md")
    content = "\n".join(
        [
            f"# {title}",
            "",
            f"- arXiv: `{paper_id}`",
            f"- Source URL: <{source_url}>",
            f"- Cached archive: `{archive_path}`",
            f"- Extracted source: `{extract_dir}`",
            f"- Entrypoint: `{entrypoint or 'not found'}`",
            f"- Authors: {', '.join(authors) if authors else 'unknown'}",
            "",
            "## 摘要总结",
            "",
            summary or "未能从可用材料中提取到足够摘要。",
            "",
            "## 核心 Insight",
            "",
            insight or "未能稳定抽取核心 insight，建议补读引言与结论。",
            "",
        ]
    )
    note_path.write_text(content, encoding="utf-8")
    return note_path


def write_daily_index(knowledge_dir: Path, target_date: str, summaries: list[PaperSummary]) -> Path:
    index_path = unique_path(knowledge_dir / f"daily_papers_{target_date}.md")
    lines = [f"# Hugging Face Daily Papers {target_date}", ""]
    for item in summaries:
        lines.extend(
            [
                f"## {item.title}",
                "",
                f"- arXiv: `{item.paper_id}`",
                f"- Authors: {', '.join(item.authors) if item.authors else 'unknown'}",
                f"- Hugging Face: <{item.hf_url}>",
                f"- Summary note: `{item.local_note}`",
                "",
                f"摘要: {item.summary}",
                "",
                f"Insight: {item.insight}",
                "",
            ]
        )
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def summarize_paper(item: dict[str, Any], prepare_source, knowledge_dir: Path) -> PaperSummary:
    paper_id = paper_id_from_item(item)
    try:
        metadata = get_json(HF_PAPER_API.format(paper_id=paper_id))
    except Exception:
        metadata = item.get("paper") if isinstance(item.get("paper"), dict) else {}
    try:
        markdown = get_text(HF_PAPER_MD.format(paper_id=paper_id))
    except Exception:
        markdown = ""
    title = metadata.get("title") or item.get("title") or paper_id
    authors = format_authors(metadata)

    helper_args = argparse.Namespace(
        paper=paper_id,
        paper_id=None,
        archive=None,
        cache_root=Path("~/.cache/nanochat/knowledge").expanduser(),
        force_download=False,
        force_extract=False,
        json=False,
    )
    prep = None
    try:
        prep = prepare_source(helper_args)
    except Exception:
        prep = None

    tex_text = ""
    if prep and prep.entrypoint:
        tex_text = collect_tex_text(Path(prep.entrypoint), Path(prep.extract_dir))

    abstract = extract_abstract(tex_text) or normalize_whitespace(metadata.get("summary") or item.get("summary") or "")
    sections = extract_section_snippets(tex_text) if tex_text else {}
    summary = choose_sentences(abstract, limit=3)
    insight = choose_insight(abstract, sections, markdown)

    note_path = write_summary_file(
        knowledge_dir=knowledge_dir,
        paper_id=paper_id,
        title=title,
        authors=authors,
        source_url=prep.src_url if prep else f"https://arxiv.org/abs/{paper_id}",
        archive_path=prep.archive_path if prep else "not available",
        extract_dir=prep.extract_dir if prep else "not available",
        entrypoint=prep.entrypoint if prep else None,
        summary=summary,
        insight=insight,
    )
    return PaperSummary(
        paper_id=paper_id,
        title=title,
        authors=authors,
        hf_url=f"https://huggingface.co/papers/{paper_id}",
        source_url=prep.src_url if prep else f"https://arxiv.org/abs/{paper_id}",
        summary=summary,
        insight=insight,
        local_note=note_path,
    )


def main() -> int:
    args = parse_args()
    prepare_source = load_prepare_source(args.helper_path)
    args.knowledge_dir.mkdir(parents=True, exist_ok=True)

    try:
        papers = fetch_daily_papers(args.date, args.limit)
    except urllib.error.URLError as exc:
        print(f"error: failed to fetch Daily Papers for {args.date}: {exc}", file=sys.stderr)
        return 2

    summaries: list[PaperSummary] = []
    for item in papers:
        try:
            summaries.append(summarize_paper(item, prepare_source, args.knowledge_dir))
        except Exception as exc:
            print(f"warn: skipped one paper because {exc}", file=sys.stderr)

    if not summaries:
        print(f"error: no summaries were written for {args.date}", file=sys.stderr)
        return 3

    index_path = write_daily_index(args.knowledge_dir, args.date, summaries)
    if args.build_site:
        subprocess.run([sys.executable, str(args.site_builder)], check=True)
    print(index_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
