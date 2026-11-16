(() => {
  'use strict';
  const slides = [...document.querySelectorAll('.slide')];
  const prev = document.querySelector('#prev');
  const next = document.querySelector('#next');
  const counter = document.querySelector('#page-number');
  let current = 0;
  function show(index, updateHash = true) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    prev.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    counter.textContent = `${current + 1} / ${slides.length}`;
    document.querySelector('#progress-fill').style.width = `${(current + 1) / slides.length * 100}%`;
    if (updateHash) history.replaceState(null, '', `#slide-${current + 1}`);
    document.title = `${current + 1}. ${slides[current].dataset.title}｜AV Speaker Wiki`;
    window.scrollTo(0, 0);
  }
  const fromHash = () => { const n = /^#slide-(\d+)$/.exec(location.hash); show(n ? Number(n[1]) - 1 : 0, false); };
  prev.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  document.addEventListener('keydown', event => {
    if (/INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    const delta = {ArrowRight: 1, ArrowDown: 1, PageDown: 1, ArrowLeft: -1, ArrowUp: -1, PageUp: -1}[event.key];
    if (delta) { event.preventDefault(); show(current + delta); }
    if (event.key === 'Home') { event.preventDefault(); show(0); }
    if (event.key === 'End') { event.preventDefault(); show(slides.length - 1); }
  });
  document.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', () => {
    document.querySelector('.quiz-feedback').textContent = button.dataset.answer === 'correct'
      ? '答對了！保留 off-screen／unknown，不強制把旁白配給畫面中的臉。'
      : '再想一想：看到一張臉，不表示聲音一定屬於他。畫外旁白可以沒有可見軌跡。';
  }));
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
