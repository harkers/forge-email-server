const API = window.FORGE_PIPELINE_API_BASE || `${window.location.origin}/api`;
const API_KEY = window.FORGE_PIPELINE_API_KEY || '';
const POLL_MS = 30000;
const PROJECT_STATUSES = [
  ['not-started', 'Not Started / Pending'],
  ['in-progress', 'In Progress / Active'],
  ['on-track', 'On Track / Green'],
  ['at-risk', 'At Risk / Yellow'],
  ['off-track', 'Off Track / Red'],
  ['blocked', 'Blocked / On Hold'],
  ['completed', 'Completed / Done'],
  ['overdue', 'Overdue'],
  ['cancelled', 'Cancelled'],
];

let state = { projects: [] };
let filters = { search: '', status: 'all', source: 'all' };
let recentEvents = [];
let isRefreshing = false;
let lastRefreshAt = null;

async function boot() {
  bindUI();
  await refresh();
  startPolling();
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
  if (isRefreshing) return;
  isRefreshing = true;
  setLiveStatus('Refreshing…');
  try {
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

    lastRefreshAt = new Date();
    populateSourceFilter();
    render();
    setLiveStatus(`Live refresh on · updated ${formatClockTime(lastRefreshAt)}`);
  } catch (err) {
    setLiveStatus(`Refresh failed · ${err}`);
    throw err;
  } finally {
    isRefreshing = false;
  }
}

function startPolling() {
  setInterval(async () => {
    try {
      await refresh();
    } catch (_) {}
  }, POLL_MS);
}

function setLiveStatus(text) {
  const el = document.getElementById('liveStatus');
  if (el) el.textContent = text;
}

function formatClockTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
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
  document.getElementById('sourceFilter').addEventListener('change', (e) => {
    filters.source = e.target.value;
    render();
  });
  document.getElementById('projectGrid').addEventListener('click', handleGridClick);
  document.getElementById('projectGrid').addEventListener('change', handleGridChange);
  document.getElementById('refreshEventsButton').addEventListener('click', refresh);
}

async function onCreateProject(event) {
  event.preventDefault();
  const fd = new FormData(event.target);
  const sourceTag = (fd.get('sourceTag') || '').trim();
  await request('/projects', {
    method: 'POST',
    body: JSON.stringify({
      name: fd.get('name'),
      status: fd.get('status') || 'in-progress',
      description: fd.get('description') || '',
      notes: fd.get('notes') || '',
      tags: sourceTag ? [sourceTag] : [],
    }),
  });
  event.target.reset();
  event.target.querySelector('[name="status"]').value = 'in-progress';
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
    let value = input.value;
    if (field === 'tags') {
      value = input.value.split(',').map(s => s.trim()).filter(Boolean);
    }
    const payload = { [field]: value };
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

function populateSourceFilter() {
  const select = document.getElementById('sourceFilter');
  const current = filters.source;
  const sources = new Set();

  for (const project of state.projects) {
    (project.tags || []).filter(isSourceTag).forEach(tag => sources.add(tag));
    for (const task of project.tasks || []) {
      (task.tags || []).filter(isSourceTag).forEach(tag => sources.add(tag));
    }
  }

  for (const event of recentEvents) {
    const source = extractEventSource(event);
    if (source) sources.add(`source:${source}`);
  }

  select.innerHTML = '<option value="all">All sources</option>' +
    [...sources].sort().map(source => `<option value="${escapeHtml(source)}">${escapeHtml(source)}</option>`).join('');

  select.value = [...sources].includes(current) ? current : 'all';
  filters.source = select.value;
}

function isSourceTag(tag) {
  return String(tag).startsWith('source:');
}

function extractEventSource(event) {
  const payload = event.payload || {};
  if (payload.source) return payload.source;
  if (payload.payload?.source) return payload.payload.source;
  return null;
}

function sourceMatchesProject(project) {
  if (filters.source === 'all') return true;
  const projectSources = new Set((project.tags || []).filter(isSourceTag));
  (project.tasks || []).forEach(task => (task.tags || []).filter(isSourceTag).forEach(tag => projectSources.add(tag)));
  return projectSources.has(filters.source);
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
  const matchesSource = filters.source === 'all' || (task.tags || []).includes(filters.source);
  return matchesSearch && matchesStatus && matchesSource;
}

function projectMatches(project) {
  const projectBlob = [project.name, project.description, project.notes, ...(project.tags || [])].join(' ').toLowerCase();
  const projectSearchHit = !filters.search || projectBlob.includes(filters.search);
  const matchingTasks = (project.tasks || []).filter(taskMatches);
  const projectSourceHit = filters.source === 'all' || (project.tags || []).includes(filters.source);
  if (!(projectSourceHit || sourceMatchesProject(project))) return false;
  return (projectSearchHit && (filters.source === 'all' || projectSourceHit)) || matchingTasks.length > 0;
}

function allTasksWithProject() {
  return state.projects.flatMap(project =>
    (project.tasks || []).map(task => ({ ...task, projectId: project.id, projectName: project.name, projectTags: project.tags || [], projectStatus: project.status }))
  );
}

function render() {
  renderDashboard();
  renderProjects();
  renderEvents();
}

function renderDashboard() {
  const tasks = allTasksWithProject().filter(task => task.projectStatus !== 'cancelled').filter(task => {
    if (filters.source === 'all') return true;
    return (task.tags || []).includes(filters.source) || (task.projectTags || []).includes(filters.source);
  });

  const nextUp = tasks
    .filter(task => task.status === 'todo' || task.status === 'in-progress')
    .sort((a, b) => scoreTask(b) - scoreTask(a))
    .slice(0, 5);

  const blocked = tasks
    .filter(task => task.status === 'blocked' || task.projectStatus === 'blocked')
    .sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''))
    .slice(0, 5);

  const recent = tasks
    .slice()
    .sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''))
    .slice(0, 5);

  renderMiniList('nextUpList', nextUp, 'No obvious next tasks yet.');
  renderMiniList('blockedList', blocked, 'Nothing blocked right now.');
  renderMiniList('recentList', recent, 'Nothing changed recently.');
}

function scoreTask(task) {
  const priorityScore = { high: 3, medium: 2, low: 1 }[task.priority] || 0;
  const statusScore = task.status === 'in-progress' ? 3 : task.status === 'todo' ? 2 : 0;
  const dueBonus = task.dueDate ? 2 : 0;
  return priorityScore * 10 + statusScore * 5 + dueBonus;
}

function renderMiniList(targetId, items, emptyText) {
  const el = document.getElementById(targetId);
  if (!items.length) {
    el.innerHTML = `<div class="empty-tasks">${emptyText}</div>`;
    return;
  }

  el.innerHTML = items.map(item => `
    <div class="mini-item">
      <div class="mini-title">${escapeHtml(item.title)}</div>
      <div class="mini-sub">${escapeHtml(item.projectName || 'Unknown project')}</div>
      <div class="mini-meta">
        <span class="badge">${escapeHtml(item.status || '')}</span>
        <span class="badge priority-${escapeHtml(item.priority || 'medium')}">${escapeHtml(item.priority || 'medium')}</span>
        ${item.dueDate ? `<span class="badge">due ${escapeHtml(item.dueDate)}</span>` : ''}
        ${collectSourceTags(item).map(tag => `<span class="badge">${escapeHtml(tag)}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

function collectSourceTags(item) {
  const tags = new Set();
  (item.tags || []).filter(isSourceTag).forEach(t => tags.add(t));
  (item.projectTags || []).filter(isSourceTag).forEach(t => tags.add(t));
  return [...tags];
}

function projectStatusBadge(status) {
  return `<span class="badge project-status status-${escapeHtml(status || 'in-progress')}">${escapeHtml(projectStatusLabel(status))}</span>`;
}

function projectStatusLabel(status) {
  return Object.fromEntries(PROJECT_STATUSES)[status] || status || 'Unknown';
}

function renderProjects() {
  const filteredProjects = state.projects.filter(project => project.status !== 'cancelled').filter(projectMatches);
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

        <div class="project-status-row">
          ${projectStatusBadge(project.status)}
          <label class="inline-select">Project status
            <select data-project-id="${project.id}" data-field="status">
              ${PROJECT_STATUSES.map(([value, label]) => `<option value="${value}" ${project.status === value ? 'selected' : ''}>${escapeHtml(label)}</option>`).join('')}
            </select>
          </label>
        </div>

        <label class="editor-label">Description
          <textarea data-project-id="${project.id}" data-field="description" rows="2">${escapeHtml(project.description || '')}</textarea>
        </label>

        <label class="editor-label">Notes
          <textarea data-project-id="${project.id}" data-field="notes" rows="5">${escapeHtml(project.notes || '')}</textarea>
        </label>

        <label class="editor-label">Project tags
          <input data-project-id="${project.id}" data-field="tags" value="${escapeHtml((project.tags || []).join(', '))}" placeholder="source:mcp-pipeline, ops" />
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
                  <input data-project-id="${project.id}" data-task-id="${task.id}" data-field="tags" value="${escapeHtml((task.tags || []).join(', '))}" placeholder="source:display-forge, ui" />
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
                ${(project.tags || []).filter(isSourceTag).map(tag => `<span class="badge">${escapeHtml(tag)}</span>`).join('')}
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
  const visibleEvents = recentEvents.filter(event => {
    if (filters.source === 'all') return true;
    const source = extractEventSource(event);
    return source ? `source:${source}` === filters.source : false;
  });

  if (!visibleEvents.length) {
    eventList.innerHTML = `<div class="empty-tasks">No recent activity yet.</div>`;
    return;
  }

  eventList.innerHTML = visibleEvents.map(event => {
    const formatted = formatEvent(event);
    return `
      <article class="event-item">
        <div class="event-kind">${escapeHtml(formatted.title)}</div>
        <div class="event-time">${escapeHtml(formatRelativeTime(event.createdAt))}</div>
        <div class="event-summary">${escapeHtml(formatted.summary)}</div>
        ${formatted.meta.length ? `<div class="event-meta">${formatted.meta.map(m => `<span class="event-chip">${escapeHtml(m)}</span>`).join('')}</div>` : ''}
      </article>
    `;
  }).join('');
}

function formatEvent(event) {
  const kind = event.kind || 'event';
  const payload = event.payload || {};

  const mappings = {
    'project.created': {
      title: 'Project created',
      summary: payload.name ? `Created project “${payload.name}”.` : 'Created a project.',
      meta: [payload.projectId].filter(Boolean),
    },
    'project.updated': {
      title: 'Project updated',
      summary: 'Updated project details.',
      meta: [payload.projectId].filter(Boolean),
    },
    'project.deleted': {
      title: 'Project deleted',
      summary: 'Removed a project.',
      meta: [payload.projectId].filter(Boolean),
    },
    'task.created': {
      title: 'Task created',
      summary: payload.title ? `Created task “${payload.title}”.` : 'Created a task.',
      meta: [payload.projectId, payload.taskId].filter(Boolean),
    },
    'task.updated': {
      title: 'Task updated',
      summary: 'Updated a task.',
      meta: [payload.projectId, payload.taskId].filter(Boolean),
    },
    'task.deleted': {
      title: 'Task deleted',
      summary: 'Removed a task.',
      meta: [payload.projectId, payload.taskId].filter(Boolean),
    },
    'bulk.import': {
      title: 'Bulk import',
      summary: `Imported ${payload.projectCount ?? 0} projects.`,
      meta: [],
    },
    'mcp.project-upsert': {
      title: 'MCP project sync',
      summary: `${capitalize(payload.action || 'updated')} project${payload.name ? ` “${payload.name}”` : ''}.`,
      meta: [payload.projectId, 'source:mcp'].filter(Boolean),
    },
    'mcp.task-upsert': {
      title: 'MCP task sync',
      summary: `${capitalize(payload.action || 'updated')} task${payload.title ? ` “${payload.title}”` : ''}.`,
      meta: [payload.projectId, payload.taskId, 'source:mcp'].filter(Boolean),
    },
    'mcp.project-update': {
      title: 'MCP project update',
      summary: payload.status ? `Updated project status to ${payload.status}.` : 'Applied project update from MCP.',
      meta: [payload.projectId, 'source:mcp'].filter(Boolean),
    },
    'webhook.project-upsert': {
      title: 'Webhook project sync',
      summary: `${capitalize(payload.action || 'updated')} project${payload.name ? ` “${payload.name}”` : ''}.`,
      meta: [payload.projectId, payload.source ? `source:${payload.source}` : null].filter(Boolean),
    },
    'webhook.task-upsert': {
      title: 'Webhook task sync',
      summary: `${capitalize(payload.action || 'updated')} task${payload.title ? ` “${payload.title}”` : ''}.`,
      meta: [payload.projectId, payload.taskId, payload.source ? `source:${payload.source}` : null].filter(Boolean),
    },
  };

  if (kind.startsWith('mcp.event.') || kind.startsWith('webhook.event.')) {
    const shortKind = kind.split('.').slice(2).join('.');
    return {
      title: `Event: ${shortKind}`,
      summary: payload.payload?.message || 'Recorded an external event.',
      meta: [payload.source ? `source:${payload.source}` : null].filter(Boolean),
    };
  }

  return mappings[kind] || {
    title: kind,
    summary: 'Recorded an event.',
    meta: Object.keys(payload).slice(0, 3).map(key => `${key}:${stringifyMeta(payload[key])}`),
  };
}

function stringifyMeta(value) {
  if (value == null) return 'null';
  if (typeof value === 'object') return 'object';
  return String(value);
}

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : value;
}

function formatRelativeTime(isoString) {
  if (!isoString) return 'unknown time';
  const then = new Date(isoString).getTime();
  const now = Date.now();
  const diffSeconds = Math.round((now - then) / 1000);
  const abs = Math.abs(diffSeconds);
  if (abs < 60) return `${abs}s ago`;
  if (abs < 3600) return `${Math.round(abs / 60)}m ago`;
  if (abs < 86400) return `${Math.round(abs / 3600)}h ago`;
  return `${Math.round(abs / 86400)}d ago`;
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
