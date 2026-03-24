async function loadData() {
  const res = await fetch('../data/sample-data.json');
  return res.json();
}

function render(data) {
  const projects = data.projects || [];
  const tasks = projects.flatMap(p => p.tasks || []);
  const open = tasks.filter(t => t.status !== 'done');

  document.getElementById('projectCount').textContent = projects.length;
  document.getElementById('taskCount').textContent = tasks.length;
  document.getElementById('openCount').textContent = open.length;

  const grid = document.getElementById('projectGrid');
  grid.innerHTML = '';

  for (const project of projects) {
    const card = document.createElement('article');
    card.className = 'project-card';
    card.innerHTML = `
      <h3>${project.name}</h3>
      <p>${project.description || ''}</p>
      <div class="notes">${project.notes || 'No notes yet.'}</div>
      <div class="task-list">
        ${(project.tasks || []).map(task => `
          <div class="task-item">
            <strong>${task.title}</strong>
            <div class="task-meta">
              <span class="badge">${task.status}</span>
              <span class="badge priority-${task.priority}">${task.priority}</span>
              ${task.dueDate ? `<span class="badge">due ${task.dueDate}</span>` : ''}
              ${(task.tags || []).map(tag => `<span class="badge">#${tag}</span>`).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;
    grid.appendChild(card);
  }
}

loadData().then(render).catch(err => {
  document.body.innerHTML = `<pre style="padding:20px;color:white;">Failed to load app data\n${err}</pre>`;
});
