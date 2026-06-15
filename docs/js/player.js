// Quiz player: loads one quiz by ?quiz=<id>, steps through questions,
// reveals answers on demand. Navigation by buttons and arrow keys; reveal by Space.
(function () {
  const els = {
    title: document.getElementById('quiz-title'),
    progress: document.getElementById('progress'),
    image: document.getElementById('question-image'),
    prompt: document.getElementById('prompt'),
    revealBtn: document.getElementById('reveal-btn'),
    answer: document.getElementById('answer'),
    answerText: document.getElementById('answer-text'),
    answerCountry: document.getElementById('answer-country'),
    prevBtn: document.getElementById('prev-btn'),
    nextBtn: document.getElementById('next-btn'),
    error: document.getElementById('error'),
  };

  let quiz = null;
  let index = 0;       // current question index
  let revealed = false;

  init();

  async function init() {
    const id = new URLSearchParams(location.search).get('quiz');
    if (!id) return showError('No quiz specified.');

    try {
      const res = await fetch(`data/${encodeURIComponent(id)}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      quiz = await res.json();
    } catch (err) {
      return showError(`Could not load this quiz (${err.message}). ` +
        'If you opened the file directly, serve it with a local web server instead.');
    }

    if (!quiz.questions || quiz.questions.length === 0) {
      return showError('This quiz has no questions.');
    }

    els.title.textContent = quiz.title || 'Quiz';
    document.title = `${quiz.title || 'Quiz'} — Soluna Quizzes`;

    els.revealBtn.addEventListener('click', reveal);
    els.prevBtn.addEventListener('click', () => go(-1));
    els.nextBtn.addEventListener('click', () => go(1));
    document.addEventListener('keydown', onKey);

    render();
  }

  function render() {
    const q = quiz.questions[index];
    revealed = false;

    els.progress.textContent = `${index + 1} / ${quiz.questions.length}`;
    els.prompt.textContent = quiz.prompt || '';
    els.image.src = q.image;
    els.image.alt = `Quiz image ${index + 1}`;

    els.answer.hidden = true;
    els.answerText.textContent = q.answer || '';
    els.answerCountry.textContent = q.country ? ` · ${q.country}` : '';
    els.revealBtn.hidden = false;

    els.prevBtn.disabled = index === 0;
    els.nextBtn.disabled = index === quiz.questions.length - 1;
  }

  function reveal() {
    if (revealed) return;
    revealed = true;
    els.answer.hidden = false;
    els.revealBtn.hidden = true;
  }

  function go(delta) {
    const next = index + delta;
    if (next < 0 || next >= quiz.questions.length) return;
    index = next;
    render();
  }

  function onKey(e) {
    if (e.key === 'ArrowRight') { go(1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft') { go(-1); e.preventDefault(); }
    else if (e.key === ' ' || e.key === 'Spacebar') { reveal(); e.preventDefault(); }
  }

  function showError(msg) {
    els.error.hidden = false;
    els.error.textContent = msg;
  }
})();
