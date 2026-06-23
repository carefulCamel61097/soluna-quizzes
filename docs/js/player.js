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
    quizEnd: document.getElementById('quiz-end'),
    doneBtn: document.getElementById('done-btn'),
  };

  // Shared with the landing page: marks live in localStorage as
  // { [quizId]: { fav: bool, done: bool } }.
  const MARKS_KEY = 'soluna-marks-v1';
  function loadMarks() {
    try { return JSON.parse(localStorage.getItem(MARKS_KEY)) || {}; }
    catch { return {}; }
  }
  function isDone(id) { return !!(loadMarks()[id] || {}).done; }
  function setDone(id, value) {
    const marks = loadMarks();
    const m = marks[id] || { fav: false, done: false };
    m.done = value;
    marks[id] = m;
    try { localStorage.setItem(MARKS_KEY, JSON.stringify(marks)); } catch {}
  }

  let quiz = null;
  let quizId = null;
  let index = 0;       // current question index
  let revealed = false;

  init();

  async function init() {
    const id = new URLSearchParams(location.search).get('quiz');
    if (!id) return showError('No quiz specified.');
    quizId = id;

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
    els.doneBtn.addEventListener('click', toggleDone);
    document.addEventListener('keydown', onKey);
    enableSwipe(document.getElementById('stage'));

    render();
  }

  // Horizontal swipe on touch screens navigates between questions.
  function enableSwipe(el) {
    if (!el) return;
    let startX = 0, startY = 0, tracking = false;
    el.addEventListener('touchstart', (e) => {
      if (e.touches.length !== 1) return;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      tracking = true;
    }, { passive: true });
    el.addEventListener('touchend', (e) => {
      if (!tracking) return;
      tracking = false;
      const dx = e.changedTouches[0].clientX - startX;
      const dy = e.changedTouches[0].clientY - startY;
      // Require a clearly horizontal swipe so vertical scrolling isn't hijacked.
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        go(dx < 0 ? 1 : -1);
      }
    }, { passive: true });
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
    const onLast = index === quiz.questions.length - 1;
    els.nextBtn.disabled = onLast;

    // Offer the "mark done" panel once the player reaches the final question.
    els.quizEnd.hidden = !onLast;
    if (onLast) renderDone();
  }

  function renderDone() {
    const done = isDone(quizId);
    els.doneBtn.classList.toggle('on', done);
    els.doneBtn.setAttribute('aria-pressed', String(done));
    els.doneBtn.textContent = done ? '✓ Marked done · tap to undo' : '✓ Mark quiz as done';
  }

  function toggleDone() {
    setDone(quizId, !isDone(quizId));
    renderDone();
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
