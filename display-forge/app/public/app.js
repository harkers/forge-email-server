async function boot() {
  const res = await fetch('../data/projects.json');
  const data = await res.json();
  const projects = data.projects || [];
  const tasks = projects.flatMap(p => p.tasks || []);

  document.getElementById('projectsCount').textContent = projects.length;
  document.getElementById('tasksCount').textContent = tasks.length;

  const grid = document.getElementById('grid');
  grid.innerHTML = projects.map(project => `
    <article class="card">
      <h2>${project.name}</h2>
      <p>${project.description || ''}</p>
      <div class="note">${project.notes || 'No notes yet.'}</div>
      <div class="tasklist">
        ${(project.tasks || []).map(task => `
          <div class="task">
            <strong>${task.title}</strong>
            <div class="meta">
              <span class="badge">${task.status}</span>
              <span class="badge">${task.priority}</span>
              ${task.dueDate ? `<span class="badge">due ${task.dueDate}</span>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    </article>
  `).join('');
}

boot().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px">${String(err)}</pre>`;
});
