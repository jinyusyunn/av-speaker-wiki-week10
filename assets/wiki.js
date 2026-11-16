(() => {
  const input = document.querySelector('#wiki-search');
  const entries = [...document.querySelectorAll('.entry')];
  function filter() {
    const terms = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    entries.forEach(entry => {
      const match = terms.every(term => entry.dataset.search.toLowerCase().includes(term));
      entry.hidden = !match;
      if (match) count++;
    });
    document.querySelector('#search-status').textContent = `${count} 個條目符合查詢`;
  }
  input.addEventListener('input', filter);
  filter();
})();
