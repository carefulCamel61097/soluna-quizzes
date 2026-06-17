// Landing page: load the quiz manifest, render a card per quiz,
// and let the player mark quizzes as Favourite / Done (stored locally in this browser).
(function () {
  const container = document.getElementById('quiz-sections');
  const STORE_KEY = 'soluna-marks-v1';
  // Theme display order; any unknown theme is appended after these.
  const THEME_ORDER = ['Geography', 'History'];

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
      container.innerHTML = `<p class="error">Could not load quizzes (${escapeHtml(String(err.message))}).
        If you opened this file directly, serve it with a local web server instead.</p>`;
    }
  }

  function render(quizzes) {
    if (quizzes.length === 0) {
      container.innerHTML = '<p class="loading">No quizzes yet.</p>';
      return;
    }

    const marks = loadMarks();
    container.innerHTML = '';

    // Group quizzes by theme, preserving manifest order within each group.
    const groups = new Map();
    for (const q of quizzes) {
      const theme = q.theme || 'Other';
      if (!groups.has(theme)) groups.set(theme, []);
      groups.get(theme).push(q);
    }
    const themes = [...groups.keys()].sort((a, b) => {
      const ia = THEME_ORDER.indexOf(a), ib = THEME_ORDER.indexOf(b);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });

    for (const theme of themes) {
      const quizzesInTheme = groups.get(theme);
      const section = document.createElement('section');
      section.className = 'theme-section';
      const heading = document.createElement('h2');
      heading.className = 'theme-heading';
      heading.innerHTML = `${escapeHtml(theme)} <span class="theme-count">${quizzesInTheme.length}</span>`;
      const list = document.createElement('ul');
      list.className = 'quiz-list';
      for (const q of quizzesInTheme) list.appendChild(buildCard(q, marks));
      section.appendChild(heading);
      section.appendChild(list);
      container.appendChild(section);
    }
  }

  function buildCard(q, marks) {
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

      return li;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
})();
