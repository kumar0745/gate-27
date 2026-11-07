(() => {
  const paperGrid = document.getElementById('paper-grid');
  const searchInput = document.getElementById('paper-search');
  const resultsLabel = document.getElementById('paper-results-label');
  const emptyState = document.getElementById('paper-empty');
  const countNode = document.getElementById('paper-count');
  const navToggle = document.getElementById('mobile-nav-toggle');
  const nav = document.getElementById('site-nav');
  let papers = [];

  const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));

  function paperCard(paper, index) {
    const code = escapeHTML(paper.code);
    const name = escapeHTML(paper.name);
    const accent = ['blue', 'mint', 'peach', 'lavender'][index % 4];
    return `<article class="paper-card ${accent}">
      <div class="paper-card-top"><span class="paper-code">${code}</span><span class="paper-card-mark" aria-hidden="true">↗</span></div>
      <h3>${name}</h3>
      <div class="paper-card-bottom"><span>GATE 2027 · ${code}</span><a href="/app?paper=${encodeURIComponent(paper.code)}" aria-label="Prepare for ${name}">Choose paper <span aria-hidden="true">→</span></a></div>
    </article>`;
  }

  function renderPapers() {
    const query = searchInput.value.trim().toLocaleLowerCase();
    const filtered = papers.filter((paper) => `${paper.code} ${paper.name}`.toLocaleLowerCase().includes(query));
    paperGrid.innerHTML = filtered.map(paperCard).join('');
    resultsLabel.textContent = query ? `${filtered.length} of ${papers.length} papers` : `${papers.length} papers available`;
    countNode.textContent = papers.length;
    emptyState.hidden = filtered.length !== 0;
    paperGrid.hidden = filtered.length === 0;
  }

  async function loadPapers() {
    try {
      const response = await fetch('/api/papers', { headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error(`Paper catalogue request failed (${response.status})`);
      const payload = await response.json();
      if (!Array.isArray(payload.items)) throw new Error('Paper catalogue format was unexpected');
      papers = payload.items;
      renderPapers();
    } catch (error) {
      paperGrid.innerHTML = `<div class="paper-error"><b>We could not load the paper catalogue.</b><span>${escapeHTML(error.message)}</span><button type="button" id="retry-papers" class="text-button">Try again</button></div>`;
      resultsLabel.textContent = 'Catalogue unavailable';
      document.getElementById('retry-papers')?.addEventListener('click', loadPapers);
    }
  }

  searchInput?.addEventListener('input', renderPapers);
  document.getElementById('clear-paper-search')?.addEventListener('click', () => {
    searchInput.value = '';
    renderPapers();
    searchInput.focus();
  });

  navToggle?.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    nav.classList.remove('is-open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }));
  document.getElementById('footer-year').textContent = String(new Date().getFullYear());

  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
      event.preventDefault();
      searchInput?.focus();
      document.getElementById('papers')?.scrollIntoView({ behavior: 'smooth' });
    }
  });

  loadPapers();
})();
