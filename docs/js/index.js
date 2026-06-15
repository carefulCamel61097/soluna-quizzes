// Landing page: load the quiz manifest and render a card per quiz.
(async function () {
  const list = document.getElementById('quiz-list');

  try {
    const res = await fetch('data/quizzes.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const quizzes = data.quizzes || [];

    if (quizzes.length === 0) {
      list.innerHTML = '<li class="loading">No quizzes yet.</li>';
      return;
    }

    list.innerHTML = '';
    for (const q of quizzes) {
      const li = document.createElement('li');
      li.className = 'quiz-card';
      const href = `player.html?quiz=${encodeURIComponent(q.id)}`;
      li.innerHTML = `
        <a class="quiz-card-link" href="${href}">
          <div class="quiz-card-thumb" style="background-image:url('${q.thumb}')"></div>
          <div class="quiz-card-body">
            <h2 class="quiz-card-title">${escapeHtml(q.title)}</h2>
            <p class="quiz-card-desc">${escapeHtml(q.description || '')}</p>
            <p class="quiz-card-meta">${q.count} questions</p>
          </div>
        </a>`;
      list.appendChild(li);
    }
  } catch (err) {
    list.innerHTML = `<li class="error">Could not load quizzes (${escapeHtml(String(err.message))}).
      If you opened this file directly, serve it with a local web server instead.</li>`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
})();
