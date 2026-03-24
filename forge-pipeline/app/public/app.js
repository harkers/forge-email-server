const API = window.FORGE_PIPELINE_API_BASE || `${window.location.origin}/api`;
const API_KEY = window.FORGE_PIPELINE_API_KEY || '';

let state = { projects: [] };
let filters = { search: '', status: 'all' };
let recentEvents = [];

async function boot() {
  bindUI();
  await refresh();
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (API_KEY) headers['X-API-Key'] = API_KEY;

  const res = await fetch(`${API}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  if (res.status === 204) return null;
  return res.json();
}

async function refresh() {
  const [summary, projectData, eventData] = await Promise.all([
    request('/summary'),
    request('/projects'),
    request('/events?limit=12'),
  ]);
  state.projects = projectData.projects || [];
  recentEvents = eventData.events || [];

  document.getElementById('projectCount').textContent = summary.projectCount;
  document.getElementById('taskCount').textContent = summary.taskCount;
  document.getElementById('openCount').textContent = summary.openTaskCount;
  document.getElementById('doneCount').textContent = summary.doneTaskCount;

  render();
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
  document.getElementById('refreshEventsButton').addEventListener('click', refresh);
}

async function onCreateProject(event) {
  event.preventDefault();
  const fd = new FormData(event.target);
  await request('/projects', {
    method: 'POST',
    body: JSON.stringify({
      name: fd.get('name'),
      description: fd.get('description') || '',
      notes: fd.get('notes') || '',
      status: 'active',
      tags: [],
    }),
  });
  event.target.reset();
  await refresh();
}

async function handleGridClick(event) {
  const actionEl = event.target.closest('[data-action]');
  if (!actionEl) return;
  const projectId = actionEl.dataset.projectId;
  const taskId = actionEl.dataset.taskId;
  const action = actionEl.dataset.action;
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;

  if (action === 'delete-project') {
    if (!confirm(`Delete project "${project.name}"?`)) return;
    await request(`/projects/${projectId}`, { method: 'DELETE' });
  }

  if (action === 'add-task') {
    await request(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify({
        title: 'New task',
        status: 'todo',
        priority: 'medium',
        dueDate: '',
        tags: [],
        notes: '',
      }),
    });
  }

  if (action === 'delete-task') {
    await request(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' });
  }

  await refresh();
}

async function handleGridChange(event) {
  const input = event.target;
  const projectId = input.dataset.projectId;
  const taskId = input.dataset.taskId;
  const field = input.dataset.field;
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;

  if (!taskId && field) {
    const payload = { [field]: input.value };
    await request(`/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    await refresh();
    return;
  }

  const task = project.tasks.find(t => t.id === taskId);
  if (!task) return;

  let value = input.value;
  if (field === 'tags') {
    value = input.value.split(',').map(s => s.trim()).filter(Boolean);
  }

  await request(`/projects/${projectId}/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ [field]: value }),
  });
  await refresh();
}

function taskMatches(task) {
  const searchBlob = [
    task.title,
    task.status,
    task.priority,
    task.dueDate,
    task.notes,
    ...(task.tags || []),
  ].join(' ').toLowerCase();

  const matchesSearch = !filters.search || searchBlob.includes(filters.search);
  const matchesStatus = filters.status === 'all' || task.status === filters.status;
  return matchesSearch && matchesStatus;
}

function projectMatches(project) {
  const projectBlob = [project.name, project.description, project.notes, ...(project.tags || [])].join(' ').toLowerCase();
  const projectSearchHit = !filters.search || projectBlob.includes(filters.search);
  const matchingTasks = (project.tasks || []).filter(taskMatches);
  return projectSearchHit || matchingTasks.length > 0;
}

function render() {
  renderProjects();
  renderEvents();
}

function renderProjects() {
  const filteredProjects = state.projects.filter(projectMatches);
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
              <label class="editor-label">Task notes
                <textarea data-project-id="${project.id}" data-task-id="${task.id}" data-field="notes" rows="3">${escapeHtml(task.notes || '')}</textarea>
              </label>
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

function renderEvents() {
  const eventList = document.getElementById('eventList');
  if (!recentEvents.length) {
    eventList.innerHTML = `<div class="empty-tasks">No recent activity yet.</div>`;
    return;
  }

  eventList.innerHTML = recentEvents.map(event => `
    <article class="event-item">
      <div class="event-kind">${escapeHtml(event.kind || 'event')}</div>
      <div class="event-time">${escapeHtml(event.createdAt || '')}</div>
      <pre class="event-payload">${escapeHtml(JSON.stringify(event.payload || {}, null, 2))}</pre>
    </article>
  `).join('');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

boot().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px;color:white;">Failed to load Forge Pipeline\n${err}</pre>`;
});
