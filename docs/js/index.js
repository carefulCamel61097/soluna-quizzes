// Landing page: load the quiz manifest, render a card per quiz,
// and let the player mark quizzes as Favourite / Done (stored locally in this browser).
(function () {
  const list = document.getElementById('quiz-list');
  const STORE_KEY = 'soluna-marks-v1';

  // --- local storage of marks: { [quizId]: { fav: bool, done: bool } } ---
  function loadMarks() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch { return {}; }
  }
  function saveMarks(marks) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(marks)); } catch {}
  }
  function getMark(marks, id) { return marks[id] || { fav: false, done: false }; }
  function setMark(id, key, value) {
    const marks = loadMarks();
    const m = getMark(marks, id);
    m[key] = value;
    marks[id] = m;
    saveMarks(marks);
  }

  init();

  async function init() {
    try {
      const res = await fetch('data/quizzes.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      render(data.quizzes || []);
    } catch (err) {
      list.innerHTML = `<li class="error">Could not load quizzes (${escapeHtml(String(err.message))}).
        If you opened this file directly, serve it with a local web server instead.</li>`;
    }
  }

  function render(quizzes) {
    if (quizzes.length === 0) {
      list.innerHTML = '<li class="loading">No quizzes yet.</li>';
      return;
    }

    const marks = loadMarks();
    list.innerHTML = '';

    for (const q of quizzes) {
      const m = getMark(marks, q.id);
      const li = document.createElement('li');
      li.className = 'quiz-card' + (m.done ? ' is-done' : '');
      li.dataset.id = q.id;

      const href = `player.html?quiz=${encodeURIComponent(q.id)}`;
      li.innerHTML = `
        <a class="quiz-card-link" href="${href}">
          <div class="quiz-card-thumb" style="background-image:url('${q.thumb}')">
            <span class="done-badge" aria-hidden="true">✓ Done</span>
          </div>
          <div class="quiz-card-body">
            <h2 class="quiz-card-title">${escapeHtml(q.title)}</h2>
            <p class="quiz-card-desc">${escapeHtml(q.description || '')}</p>
            <p class="quiz-card-meta">${q.count} questions</p>
          </div>
        </a>
        <div class="quiz-card-marks">
          <button type="button" class="mark-btn mark-fav${m.fav ? ' on' : ''}"
            aria-pressed="${m.fav}">
            <span class="mark-icon">${m.fav ? '★' : '☆'}</span> Favourite
          </button>
          <button type="button" class="mark-btn mark-done${m.done ? ' on' : ''}"
            aria-pressed="${m.done}">
            <span class="mark-icon">${m.done ? '✓' : '○'}</span> Done
          </button>
        </div>`;

      const favBtn = li.querySelector('.mark-fav');
      const doneBtn = li.querySelector('.mark-done');

      favBtn.addEventListener('click', () => {
        const on = !favBtn.classList.contains('on');
        favBtn.classList.toggle('on', on);
        favBtn.setAttribute('aria-pressed', String(on));
        favBtn.querySelector('.mark-icon').textContent = on ? '★' : '☆';
        setMark(q.id, 'fav', on);
      });

      doneBtn.addEventListener('click', () => {
        const on = !doneBtn.classList.contains('on');
        doneBtn.classList.toggle('on', on);
        doneBtn.setAttribute('aria-pressed', String(on));
        doneBtn.querySelector('.mark-icon').textContent = on ? '✓' : '○';
        li.classList.toggle('is-done', on);
        setMark(q.id, 'done', on);
      });

      list.appendChild(li);
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
})();
