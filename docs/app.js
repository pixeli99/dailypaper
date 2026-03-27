(() => {
  const searchInput = document.querySelector("#paper-search");
  const preferredToggle = document.querySelector("#preferred-toggle");
  const tagButtons = Array.from(document.querySelectorAll(".topic-filter-row .topic-pill"));
  const cards = Array.from(document.querySelectorAll(".paper-card"));
  const emptyState = document.querySelector("#empty-state");

  if (!cards.length || !searchInput || !preferredToggle) {
    return;
  }

  let activeTag = "";
  let preferredOnly = false;

  const applyFilters = () => {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const title = card.dataset.title || "";
      const tags = card.dataset.tags || "";
      const isPreferred = card.dataset.preferred === "true";
      const matchesQuery = !query || title.includes(query) || tags.includes(query);
      const matchesTag = !activeTag || tags.includes(activeTag.toLowerCase());
      const matchesPreferred = !preferredOnly || isPreferred;
      const show = matchesQuery && matchesTag && matchesPreferred;
      card.hidden = !show;
      if (show) {
        visible += 1;
      }
    });

    if (emptyState) {
      emptyState.hidden = visible !== 0;
    }
  };

  searchInput.addEventListener("input", applyFilters);

  preferredToggle.addEventListener("click", () => {
    preferredOnly = !preferredOnly;
    preferredToggle.classList.toggle("is-active", preferredOnly);
    applyFilters();
  });

  tagButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextTag = button.dataset.tag || "";
      activeTag = activeTag === nextTag ? "" : nextTag;
      tagButtons.forEach((item) => item.classList.toggle("is-active", item.dataset.tag === activeTag));
      applyFilters();
    });
  });
})();
