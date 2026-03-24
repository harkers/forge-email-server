const STORAGE_KEY = 'forge-pipeline-data-v1';
const DATA_URL = '../data/sample-data.json';

let state = { projects: [] };
let filters = { search: '', status: 'all' };

async function boot() {
  state = await loadState();
  bindUI();
  render();
}

async function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (_) {}
  }
  const res = await fetch(DATA_URL);
  return res.json();
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function uid(prefix = 'id') {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

function bindUI() {
  document.getElementById('projectForm').addEventListener('submit', onCreateProject);
  document.getElementById('searchInput').addEventListener('input', (e) => {
    filters.search = e.target.value.trim().toLowerCase();
    render();
  });
  document.getElementById('statusFilter').addEventListener('change', (e) => {
    filters.status = e.target.value;
    render();
  });
  document.getElementById('projectGrid').addEventListener('click', handleGridClick);
  document.getElementById('projectGrid').addEventListener('change', handleGridChange);
}

function onCreateProject(event) {
  event.preventDefault();
  const fd = new FormData(event.target);
  state.projects.unshift({
    id: uid('project'),
    name: fd.get('name'),
    description: fd.get('description') || '',
    notes: fd.get('notes') || '',
    tasks: [],
  });
  event.target.reset();
  persist();
  render();
}

function handleGridClick(event) {
  const actionEl = event.target.closest('[data-action]');
  if (!actionEl) return;
  const projectId = actionEl.dataset.projectId;
  const taskId = actionEl.dataset.taskId;
  const action = actionEl.dataset.action;
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;

  if (action === 'delete-project') {
    if (!confirm(`Delete project "${project.name}"?`)) return;
    state.projects = state.projects.filter(p => p.id !== projectId);
  }

  if (action === 'add-task') {
    project.tasks.unshift({
      id: uid('task'),
      title: 'New task',
      status: 'todo',
      priority: 'medium',
      dueDate: '',
      tags: [],
    });
  }

  if (action === 'delete-task') {
    project.tasks = project.tasks.filter(t => t.id !== taskId);
  }

  persist();
  render();
}

function handleGridChange(event) {
  const input = event.target;
  const projectId = input.dataset.projectId;
  const taskId = input.dataset.taskId;
  const field = input.dataset.field;
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;

  if (!taskId && field) {
    project[field] = input.value;
    persist();
    render();
    return;
  }

  const task = project.tasks.find(t => t.id === taskId);
  if (!task) return;

  if (field === 'tags') {
    task.tags = input.value.split(',').map(s => s.trim()).filter(Boolean);
  } else {
    task[field] = input.value;
  }

  persist();
  render();
}

function taskMatches(task) {
  const searchBlob = [
    task.title,
    task.status,
    task.priority,
    task.dueDate,
    ...(task.tags || []),
  ].join(' ').toLowerCase();

  const matchesSearch = !filters.search || searchBlob.includes(filters.search);
  const matchesStatus = filters.status === 'all' || task.status === filters.status;
  return matchesSearch && matchesStatus;
}

function projectMatches(project) {
  const projectBlob = [project.name, project.description, project.notes].join(' ').toLowerCase();
  const projectSearchHit = !filters.search || projectBlob.includes(filters.search);
  const matchingTasks = (project.tasks || []).filter(taskMatches);
  return projectSearchHit || matchingTasks.length > 0;
}

function render() {
  const projects = state.projects || [];
  const allTasks = projects.flatMap(p => p.tasks || []);
  const open = allTasks.filter(t => t.status !== 'done');
  const done = allTasks.filter(t => t.status === 'done');

  document.getElementById('projectCount').textContent = projects.length;
  document.getElementById('taskCount').textContent = allTasks.length;
  document.getElementById('openCount').textContent = open.length;
  document.getElementById('doneCount').textContent = done.length;

  const filteredProjects = projects.filter(projectMatches);
  const grid = document.getElementById('projectGrid');

  if (!filteredProjects.length) {
    grid.innerHTML = `<div class="empty-state">No matching projects yet. Try adding one or clearing the filters.</div>`;
    return;
  }

  grid.innerHTML = filteredProjects.map(project => {
    const visibleTasks = (project.tasks || []).filter(taskMatches);
    return `
      <article class="project-card">
        <div class="project-head">
          <input class="project-name-input" data-project-id="${project.id}" data-field="name" value="${escapeHtml(project.name || '')}" />
          <button class="icon-button danger" data-action="delete-project" data-project-id="${project.id}">Delete</button>
        </div>

        <label class="editor-label">Description
          <textarea data-project-id="${project.id}" data-field="description" rows="2">${escapeHtml(project.description || '')}</textarea>
        </label>

        <label class="editor-label">Notes
          <textarea data-project-id="${project.id}" data-field="notes" rows="5">${escapeHtml(project.notes || '')}</textarea>
        </label>

        <div class="project-actions">
          <button data-action="add-task" data-project-id="${project.id}">Add task</button>
          <span class="project-meta">${visibleTasks.length} shown / ${(project.tasks || []).length} total</span>
        </div>

        <div class="task-list">
          ${visibleTasks.length ? visibleTasks.map(task => `
            <div class="task-item">
              <div class="task-top">
                <input class="task-title-input" data-project-id="${project.id}" data-task-id="${task.id}" data-field="title" value="${escapeHtml(task.title || '')}" />
                <button class="icon-button danger small" data-action="delete-task" data-project-id="${project.id}" data-task-id="${task.id}">Delete</button>
              </div>
              <div class="task-edit-grid">
                <label>Status
                  <select data-project-id="${project.id}" data-task-id="${task.id}" data-field="status">
                    ${['todo','in-progress','blocked','done'].map(s => `<option value="${s}" ${task.status === s ? 'selected' : ''}>${s}</option>`).join('')}
                  </select>
                </label>
                <label>Priority
                  <select data-project-id="${project.id}" data-task-id="${task.id}" data-field="priority">
                    ${['low','medium','high'].map(s => `<option value="${s}" ${task.priority === s ? 'selected' : ''}>${s}</option>`).join('')}
                  </select>
                </label>
                <label>Due
                  <input type="date" data-project-id="${project.id}" data-task-id="${task.id}" data-field="dueDate" value="${escapeHtml(task.dueDate || '')}" />
                </label>
                <label>Tags
                  <input data-project-id="${project.id}" data-task-id="${task.id}" data-field="tags" value="${escapeHtml((task.tags || []).join(', '))}" placeholder="ops, urgent, ui" />
                </label>
              </div>
              <div class="task-meta">
                <span class="badge">${task.status}</span>
                <span class="badge priority-${task.priority}">${task.priority}</span>
                ${task.dueDate ? `<span class="badge">due ${task.dueDate}</span>` : ''}
                ${(task.tags || []).map(tag => `<span class="badge">#${escapeHtml(tag)}</span>`).join('')}
              </div>
            </div>
          `).join('') : `<div class="empty-tasks">No tasks match the current filters.</div>`}
        </div>
      </article>
    `;
  }).join('');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

boot().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px;color:white;">Failed to load app data\n${err}</pre>`;
});
