const API = window.FORGE_PIPELINE_API_BASE || `${window.location.origin}/api`;
const API_KEY = window.FORGE_PIPELINE_API_KEY || '';
const WS_URL = window.FORGE_PIPELINE_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
const POLL_MS = 30000;
const VERSION = '2.0.0';
const BUILD_DATE = '2026-03-25';
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
const KANBAN_COLUMNS = ['todo', 'in-progress', 'blocked', 'done'];

let state = { projects: [] };
let filters = { search: '', status: 'all', source: 'all', viewMode: 'portfolio', priority: 'all', risk: 'all', sort: 'priority-desc', density: 'comfortable' };
let recentEvents = [];
let isRefreshing = false;
let lastRefreshAt = null;
let ws = null;
let wsReconnectAttempts = 0;
let wsMaxReconnectAttempts = 5;
let wsReconnectDelay = 1000;

// FP-094: WebSocket connection with graceful fallback
function connectWebSocket() {
  if (!window.WebSocket) {
    console.log('[WS] WebSocket not supported, using polling');
    return false;
  }
  
  try {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
      console.log('[WS] Connected');
      wsReconnectAttempts = 0;
      wsReconnectDelay = 1000;
      setLiveStatus('Live (WebSocket)');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'connected') {
          console.log('[WS] Server confirmed connection');
        } else if (data.type === 'pong') {
          // Heartbeat response
        } else {
          // Data update event - refresh
          console.log('[WS] Event:', data.type);
          refresh();
        }
      } catch (e) {
        console.error('[WS] Parse error:', e);
      }
    };
    
    ws.onclose = (event) => {
      console.log('[WS] Disconnected:', event.code, event.reason);
      ws = null;
      // Fallback to polling
      setLiveStatus('Live refresh on · polling');
      startPolling();
    };
    
    ws.onerror = (error) => {
      console.error('[WS] Error:', error);
      ws.close();
    };
    
    return true;
  } catch (e) {
    console.error('[WS] Connection failed:', e);
    return false;
  }
}

function tryReconnectWebSocket() {
  if (ws || wsReconnectAttempts >= wsMaxReconnectAttempts) {
    return;
  }
  
  wsReconnectAttempts++;
  console.log(`[WS] Reconnecting (${wsReconnectAttempts}/${wsMaxReconnectAttempts})...`);
  
  setTimeout(() => {
    if (!connectWebSocket()) {
      tryReconnectWebSocket();
    }
  }, wsReconnectDelay);
  
  wsReconnectDelay = Math.min(wsReconnectDelay * 2, 30000);
}

// Heartbeat to keep connection alive
function startHeartbeat() {
  setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000);
}

async function boot() {
  bindUI();
  await refresh();
  
  // FP-094: Try WebSocket first, fall back to polling
  if (!connectWebSocket()) {
    console.log('[WS] WebSocket unavailable, using polling');
    startPolling();
  } else {
    startHeartbeat();
  }
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
    document.getElementById('activeCount').textContent = summary.activeTaskCount;
    document.getElementById('doneCount').textContent = summary.doneTaskCount;
    document.getElementById('blockedCount').textContent = summary.blockedTaskCount;
    document.getElementById('atRiskCount').textContent = summary.atRiskTaskCount;
    
    // FP-011: Display deltas if available
    if (summary.deltas) {
      updateMetricDelta('activeCount', summary.deltas.activeTaskCount);
      updateMetricDelta('doneCount', summary.deltas.doneTaskCount);
      updateMetricDelta('blockedCount', summary.deltas.blockedTaskCount);
      updateMetricDelta('atRiskCount', summary.deltas.atRiskTaskCount);
    }

    lastRefreshAt = new Date();
    populateSourceFilter();
    render();
    renderVersionInfo();
    setLiveStatus(`Live refresh on · updated ${formatClockTime(lastRefreshAt)}`);
  } catch (err) {
    setLiveStatus(`Refresh failed · ${err}`);
    throw err;
  } finally {
    isRefreshing = false;
  }
}

function updateMetricDelta(elementId, delta) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const parent = el.closest('.metric');
  if (!parent) return;
  
  // Remove existing delta
  const existingDelta = parent.querySelector('.delta');
  if (existingDelta) existingDelta.remove();
  
  if (delta === 0) return;
  
  const deltaEl = document.createElement('span');
  deltaEl.className = 'delta ' + (delta > 0 ? 'positive' : 'negative');
  deltaEl.textContent = (delta > 0 ? '+' : '') + delta;
  parent.appendChild(deltaEl);
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

function renderVersionInfo() {
  const versionEl = document.getElementById('versionBadge');
  const infoEl = document.getElementById('versionInfo');
  if (versionEl) versionEl.textContent = `v${VERSION}`;
  if (infoEl && lastRefreshAt) {
    const age = Math.floor((Date.now() - lastRefreshAt) / 1000);
    const health = age < 120 ? 'healthy' : age < 300 ? 'delayed' : 'stale';
    const healthIcon = health === 'healthy' ? '✓' : health === 'delayed' ? '⏳' : '⚠';
    const healthClass = health === 'healthy' ? 'health-ok' : health === 'delayed' ? 'health-warn' : 'health-error';
    infoEl.innerHTML = `<span class="source-health ${healthClass}">${healthIcon}</span> Last updated: ${lastRefreshAt.toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })}`;
  }
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
  document.getElementById('viewMode').addEventListener('change', (e) => {
    filters.viewMode = e.target.value;
    render();
  });
  document.getElementById('priorityFilter').addEventListener('change', (e) => {
    filters.priority = e.target.value;
    render();
  });
  document.getElementById('riskFilter').addEventListener('change', (e) => {
    filters.risk = e.target.value;
    render();
  });
  document.getElementById('sortOrder').addEventListener('change', (e) => {
    filters.sort = e.target.value;
    render();
  });
  // FP-064: Density toggle
  document.querySelectorAll('.density-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.density-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      filters.density = e.target.id.replace('density', '').toLowerCase();
      document.body.dataset.density = filters.density;
      render();
    });
  });
  document.getElementById('projectGrid').addEventListener('click', handleGridClick);
  document.getElementById('projectGrid').addEventListener('change', handleGridChange);
  document.getElementById('refreshEventsButton').addEventListener('click', refresh);
  
  // FP-061: Task Detail Drawer
  document.getElementById('drawerClose').addEventListener('click', closeDrawer);
  document.getElementById('drawerCancel').addEventListener('click', closeDrawer);
  document.getElementById('drawerSave').addEventListener('click', saveDrawerChanges);
  
  // FP-091: Dependency Panel
  document.getElementById('closeDependencyBtn').addEventListener('click', closeDependencyPanel);
  
  // FP-093: View mode toggle
  setupViewModeToggle();
}

// FP-061: Task Detail Drawer
let currentDrawerTask = null;
let currentDrawerProject = null;

function openTaskDrawer(projectId, taskId) {
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;
  const task = project.tasks.find(t => t.id === taskId);
  if (!task) return;
  
  currentDrawerTask = task;
  currentDrawerProject = project;
  
  const drawer = document.getElementById('taskDrawer');
  const title = document.getElementById('drawerTitle');
  const content = document.getElementById('drawerContent');
  
  title.textContent = task.title || 'Task Details';
  content.innerHTML = `
    <div class="drawer-field">
      <label>Title</label>
      <input id="drawerTitleInput" value="${escapeHtml(task.title || '')}" />
    </div>
    <div class="drawer-field">
      <label>Status</label>
      <select id="drawerStatusInput">
        ${['todo','in-progress','blocked','done'].map(s => `<option value="${s}" ${task.status === s ? 'selected' : ''}>${s}</option>`).join('')}
      </select>
    </div>
    <div class="drawer-field">
      <label>Priority</label>
      <select id="drawerPriorityInput">
        ${['low','medium','high','critical'].map(s => `<option value="${s}" ${task.priority === s ? 'selected' : ''}>${s}</option>`).join('')}
      </select>
    </div>
    <div class="drawer-field">
      <label>Risk State</label>
      <select id="drawerRiskInput">
        ${['none','watch','at-risk','critical'].map(s => `<option value="${s}" ${(task.riskState || 'none') === s ? 'selected' : ''}>${s}</option>`).join('')}
      </select>
    </div>
    <div class="drawer-field">
      <label>Due Date</label>
      <input type="date" id="drawerDueInput" value="${task.dueDate || ''}" />
    </div>
    <div class="drawer-field">
      <label>Tags</label>
      <input id="drawerTagsInput" value="${escapeHtml((task.tags || []).join(', '))}" placeholder="source:x, component:y" />
    </div>
    <div class="drawer-field">
      <label>Notes</label>
      <textarea id="drawerNotesInput" rows="4">${escapeHtml(task.notes || '')}</textarea>
    </div>
  `;
  
  drawer.style.display = 'flex';
}

function closeDrawer() {
  document.getElementById('taskDrawer').style.display = 'none';
  currentDrawerTask = null;
  currentDrawerProject = null;
}

async function saveDrawerChanges() {
  if (!currentDrawerTask || !currentDrawerProject) return;
  
  const payload = {
    title: document.getElementById('drawerTitleInput').value,
    status: document.getElementById('drawerStatusInput').value,
    priority: document.getElementById('drawerPriorityInput').value,
    riskState: document.getElementById('drawerRiskInput').value,
    dueDate: document.getElementById('drawerDueInput').value,
    tags: document.getElementById('drawerTagsInput').value.split(',').map(s => s.trim()).filter(Boolean),
    notes: document.getElementById('drawerNotesInput').value,
  };
  
  await request(`/projects/${currentDrawerProject.id}/tasks/${currentDrawerTask.id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  
  closeDrawer();
  await refresh();
}

// FP-062: Quick Actions
function handleQuickAction(action, projectId, taskId) {
  const project = state.projects.find(p => p.id === projectId);
  if (!project) return;
  const task = project.tasks.find(t => t.id === taskId);
  if (!task) return;
  
  switch (action) {
    case 'edit':
      openTaskDrawer(projectId, taskId);
      break;
    case 'done':
      quickUpdateTask(projectId, taskId, { status: 'done' });
      break;
    case 'block':
      quickUpdateTask(projectId, taskId, { status: 'blocked' });
      break;
    case 'start':
      quickUpdateTask(projectId, taskId, { status: 'in-progress' });
      break;
    case 'delete':
      if (confirm(`Delete task "${task.title}"?`)) {
        deleteTask(projectId, taskId);
      }
      break;
  }
}

async function quickUpdateTask(projectId, taskId, updates) {
  await request(`/projects/${projectId}/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  await refresh();
}

async function deleteTask(projectId, taskId) {
  await request(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' });
  await refresh();
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

  // FP-062: Quick actions
  if (action === 'quick-edit') {
    openTaskDrawer(projectId, taskId);
    return;
  }

  if (action === 'quick-done') {
    await request(`/projects/${projectId}/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: 'done' }),
    });
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
  const matchesPriority = filters.priority === 'all' || task.priority === filters.priority;
  const matchesRisk = filters.risk === 'all' || (task.riskState || 'none') === filters.risk;
  return matchesSearch && matchesStatus && matchesSource && matchesPriority && matchesRisk;
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

function portfolioSectionFor(project) {
  const tags = new Set(project.tags || []);
  const name = (project.name || '').toLowerCase();

  if (tags.has('finance') || name.includes('finance') || name.includes('accountant')) return 'Finance & Operations';
  if (tags.has('business-concept') || tags.has('strategy') || name.includes('orderededge')) return 'Concepts & Strategy';
  if (tags.has('privacy') || tags.has('compliance') || name.includes('dsar')) return 'Privacy & Governance';
  if (tags.has('calendar') || tags.has('crm') || tags.has('platform') || tags.has('signage') || name.includes('forge')) return 'Products & Platforms';
  return 'Other Workstreams';
}

function render() {
  renderDashboard();
  renderInsightStrip();
  renderFocusNow();
  renderSourceHealth();
  renderMainPanelHeader();
  if (filters.viewMode === 'kanban') {
    renderKanban();
  } else {
    renderPortfolioProjects();
  }
  renderEvents();
}

// FP-051: Insight Strip
function renderInsightStrip() {
  const tasks = allTasksWithProject().filter(task => task.projectStatus !== 'cancelled');
  const now = new Date();
  const oneWeek = 7 * 24 * 60 * 60 * 1000;
  
  // High priority due this week
  const highPriorityDue = tasks.filter(task => {
    if (task.status === 'done') return false;
    if (task.priority !== 'critical' && task.priority !== 'high') return false;
    if (!task.dueDate) return false;
    const due = new Date(task.dueDate);
    return due <= new Date(now.getTime() + oneWeek);
  });
  
  // Active blockers
  const blockers = tasks.filter(task => task.status === 'blocked');
  
  // Stale items (>7 days since update, not done)
  const stale = tasks.filter(task => {
    if (task.status === 'done') return false;
    if (!task.updatedAt) return false;
    const updated = new Date(task.updatedAt);
    return (now - updated) > oneWeek;
  });
  
  // At risk
  const atRisk = tasks.filter(task => {
    if (task.status === 'done') return false;
    return task.riskState === 'at-risk' || task.riskState === 'critical';
  });
  
  // Update DOM
  document.getElementById('insightHighPriority').querySelector('.insight-value').textContent = highPriorityDue.length;
  document.getElementById('insightBlockers').querySelector('.insight-value').textContent = blockers.length;
  document.getElementById('insightStale').querySelector('.insight-value').textContent = stale.length;
  document.getElementById('insightAtRisk').querySelector('.insight-value').textContent = atRisk.length;
  
  // Add warning classes
  document.getElementById('insightHighPriority').classList.toggle('danger', highPriorityDue.length > 0);
  document.getElementById('insightBlockers').classList.toggle('danger', blockers.length > 0);
  document.getElementById('insightStale').classList.toggle('warning', stale.length > 0);
  document.getElementById('insightAtRisk').classList.toggle('danger', atRisk.length > 0);
}

// FP-090: Enhanced Focus Now Recommendation Engine
function calculateTaskScore(task, now = new Date()) {
  let score = 0;
  const reasons = [];
  
  // Priority scoring (0-40 points)
  const priorityScores = { critical: 40, high: 25, medium: 10, low: 5 };
  score += priorityScores[task.priority] || 0;
  if (task.priority === 'critical') reasons.push('Critical priority');
  
  // Status scoring (0-30 points)
  if (task.status === 'blocked') {
    score += 30;
    reasons.push('Blocked');
  } else if (task.status === 'in-progress') {
    score += 5; // Small boost for in-progress tasks
  }
  
  // Risk state scoring (0-25 points)
  const riskScores = { critical: 25, 'at-risk': 20, watch: 10, none: 0 };
  score += riskScores[task.riskState] || 0;
  if (task.riskState === 'critical') reasons.push('Critical risk');
  else if (task.riskState === 'at-risk') reasons.push('At risk');
  
  // Due date scoring (0-30 points, increasing as deadline approaches)
  if (task.dueDate) {
    const due = new Date(task.dueDate);
    const daysUntilDue = (due - now) / (1000 * 60 * 60 * 24);
    
    if (daysUntilDue < 0) {
      score += 30; // Overdue
      reasons.push(`Overdue by ${Math.abs(Math.round(daysUntilDue))}d`);
    } else if (daysUntilDue < 1) {
      score += 25; // Due today
      reasons.push('Due today');
    } else if (daysUntilDue < 3) {
      score += 20; // Due in 1-2 days
      reasons.push('Due soon');
    } else if (daysUntilDue < 7) {
      score += 10; // Due this week
    }
  }
  
  // Staleness penalty (deduct for tasks not updated recently)
  if (task.updatedAt) {
    const lastUpdate = new Date(task.updatedAt);
    const daysSinceUpdate = (now - lastUpdate) / (1000 * 60 * 60 * 24);
    if (daysSinceUpdate > 14) {
      score += 5; // Slight boost - stale tasks need attention
      reasons.push(`Stale (${Math.round(daysSinceUpdate)}d)`);
    }
  }
  
  return { score, reasons };
}

function findFocusCandidates(tasks, now = new Date()) {
  // Score all tasks
  const scoredTasks = tasks
    .filter(t => t.projectStatus !== 'cancelled' && t.status !== 'done')
    .map(task => {
      const { score, reasons } = calculateTaskScore(task, now);
      return { ...task, focusScore: score, focusReasons: reasons };
    })
    .sort((a, b) => b.focusScore - a.focusScore);
  
  // Group by primary reason for display
  const groups = [
    { filter: t => t.priority === 'critical', reason: 'Critical priority', icon: '🔴' },
    { filter: t => t.status === 'blocked', reason: 'Needs unblocking', icon: '🚫' },
    { filter: t => t.riskState === 'critical' || t.riskState === 'at-risk', reason: 'At risk', icon: '⚠️' },
    { filter: t => t.dueDate && new Date(t.dueDate) < now, reason: 'Overdue', icon: '🔥' },
    { filter: t => t.focusReasons.some(r => r.includes('Due today')), reason: 'Due today', icon: '📅' },
    { filter: t => t.focusReasons.some(r => r.includes('Stale')), reason: 'Needs attention', icon: '📝' },
  ];
  
  const candidates = [];
  for (const group of groups) {
    const matching = scoredTasks.filter(group.filter);
    if (matching.length > 0) {
      candidates.push({
        tasks: matching.slice(0, 5),
        reason: group.reason,
        icon: group.icon,
        totalScore: matching.reduce((sum, t) => sum + t.focusScore, 0)
      });
    }
  }
  
  return { candidates, topTasks: scoredTasks.slice(0, 5) };
}

// FP-052: Focus Now
function renderFocusNow() {
  const tasks = allTasksWithProject();
  const now = new Date();
  const panel = document.getElementById('focusNowPanel');
  const content = document.getElementById('focusContent');
  const reason = document.getElementById('focusReason');
  
  const { candidates, topTasks } = findFocusCandidates(tasks, now);
  
  if (candidates.length === 0) {
    panel.style.display = 'none';
    return;
  }
  
  panel.style.display = 'block';
  const topCandidate = candidates[0];
  reason.textContent = topCandidate.reason;
  
  // Render top 3 focus items with scores
  content.innerHTML = topTasks.slice(0, 3).map(task => `
    <div class="focus-task" data-project-id="${task.projectId}" data-task-id="${task.id}" onclick="scrollToTask('${task.projectId}', '${task.id}')">
      <span class="focus-task-title">${escapeHtml(task.title)}</span>
      <span class="focus-task-project">${escapeHtml(task.projectName || 'Unknown')}</span>
      <div class="focus-task-badges">
        ${task.priority === 'critical' ? '<span class="badge priority-critical">critical</span>' : ''}
        ${task.priority === 'high' ? '<span class="badge priority-high">high</span>' : ''}
        ${task.status === 'blocked' ? '<span class="badge status-blocked">blocked</span>' : ''}
        ${task.riskState && task.riskState !== 'none' ? `<span class="badge risk-${task.riskState}">${task.riskState}</span>` : ''}
      </div>
      <span class="focus-score" title="Focus score: ${task.focusScore}">${task.focusScore}</span>
    </div>
  `).join('');
}

function scrollToTask(projectId, taskId) {
  // Close drawer if open
  closeDrawer();
  // Find and highlight the task
  const taskEl = document.querySelector(`[data-project-id="${projectId}"][data-task-id="${taskId}"]`);
  if (taskEl) {
    taskEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    taskEl.classList.add('highlight');
    setTimeout(() => taskEl.classList.remove('highlight'), 2000);
  }
}

function allTasksWithProject() {
  return state.projects.flatMap(project => 
    (project.tasks || []).map(task => ({
      ...task,
      projectId: project.id,
      projectName: project.name,
      projectStatus: project.status,
      projectTags: project.tags || []
    }))
  );
}

// FP-054: Source Health Panel
function renderSourceHealth() {
  const sources = new Map();
  const now = new Date();
  const oneWeek = 7 * 24 * 60 * 60 * 1000;
  
  // Collect sources from projects and tasks
  for (const project of state.projects) {
    const projectSources = (project.tags || []).filter(isSourceTag);
    for (const source of projectSources) {
      if (!sources.has(source)) {
        sources.set(source, { count: 0, projects: 0, lastUpdate: null });
      }
      const data = sources.get(source);
      data.projects++;
      data.count += (project.tasks || []).length;
      if (project.updatedAt) {
        const updated = new Date(project.updatedAt);
        if (!data.lastUpdate || updated > data.lastUpdate) {
          data.lastUpdate = updated;
        }
      }
    }
    
    for (const task of project.tasks || []) {
      const taskSources = (task.tags || []).filter(isSourceTag);
      for (const source of taskSources) {
        if (!sources.has(source)) {
          sources.set(source, { count: 0, projects: 0, lastUpdate: null });
        }
        const data = sources.get(source);
        data.count++;
        if (task.updatedAt) {
          const updated = new Date(task.updatedAt);
          if (!data.lastUpdate || updated > data.lastUpdate) {
            data.lastUpdate = updated;
          }
        }
      }
    }
  }
  
  const container = document.getElementById('sourceList');
  if (!container) return;
  
  if (sources.size === 0) {
    container.innerHTML = '<div class="source-item"><span class="source-name">No sources yet</span></div>';
    return;
  }
  
  const sortedSources = [...sources.entries()].sort((a, b) => b[1].count - a[1].count);
  
  container.innerHTML = sortedSources.map(([source, data]) => {
    let healthClass = 'healthy';
    if (data.lastUpdate) {
      const age = now - data.lastUpdate;
      if (age > oneWeek) healthClass = 'warning';
      if (age > 2 * oneWeek) healthClass = 'danger';
    }
    const displayName = source.replace('source:', '');
    return `
      <div class="source-item ${healthClass}">
        <span class="source-name">${escapeHtml(displayName)}</span>
        <span class="source-count">${data.count} tasks · ${data.projects} project${data.projects !== 1 ? 's' : ''}</span>
      </div>
    `;
  }).join('');
}

function renderMainPanelHeader() {
  const title = document.getElementById('mainPanelTitle');
  const subtitle = document.getElementById('mainPanelSubtitle');
  if (filters.viewMode === 'kanban') {
    title.textContent = 'Kanban Board';
    subtitle.textContent = 'See tasks arranged by status columns across the visible portfolio.';
  } else {
    title.textContent = 'Projects';
    subtitle.textContent = 'Track what’s moving, blocked, or done — and keep the notes close to the work.';
  }
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
  const priorityScore = { critical: 4, high: 3, medium: 2, low: 1 }[task.priority] || 0;
  const riskScore = { critical: 3, 'at-risk': 2, watch: 1, none: 0 }[task.riskState] || 0;
  const statusScore = task.status === 'in-progress' ? 3 : task.status === 'todo' ? 2 : 0;
  const dueBonus = task.dueDate ? 2 : 0;
  return priorityScore * 10 + riskScore * 5 + statusScore * 3 + dueBonus;
}

// FP-063: Sorting logic
function sortTasks(tasks) {
  const sorted = [...tasks];
  const [field, direction] = (filters.sort || 'priority-desc').split('-');
  
  sorted.sort((a, b) => {
    let cmp = 0;
    
    if (field === 'priority') {
      const pa = { critical: 4, high: 3, medium: 2, low: 1 }[a.priority] || 0;
      const pb = { critical: 4, high: 3, medium: 2, low: 1 }[b.priority] || 0;
      cmp = pa - pb;
    } else if (field === 'due') {
      const da = a.dueDate ? new Date(a.dueDate).getTime() : Infinity;
      const db = b.dueDate ? new Date(b.dueDate).getTime() : Infinity;
      cmp = da - db;
    } else if (field === 'updated') {
      const ua = a.updatedAt ? new Date(a.updatedAt).getTime() : 0;
      const ub = b.updatedAt ? new Date(b.updatedAt).getTime() : 0;
      cmp = ua - ub;
    }
    
    return direction === 'desc' ? -cmp : cmp;
  });
  
  return sorted;
}

function renderMiniList(targetId, items, emptyText) {
  const el = document.getElementById(targetId);
  if (!items.length) {
    el.innerHTML = `<div class="empty-tasks">${emptyText}</div>`;
    return;
  }

  el.innerHTML = items.map(item => {
    // FP-020: Reduce metadata chip overload - show only essential badges
    // FP-021/022/023: Add overdue/due-soon/stale visual states
    const badges = [];
    const stateClasses = [];
    
    // Priority badge (only high/critical)
    if (item.priority === 'critical' || item.priority === 'high') {
      badges.push(`<span class="badge priority-${escapeHtml(item.priority)}">${escapeHtml(item.priority)}</span>`);
    }
    
    // Status badge (only blocked)
    if (item.status === 'blocked') {
      badges.push(`<span class="badge status-blocked">blocked</span>`);
    }
    
    // Risk state badge (at-risk/critical)
    if (item.riskState && item.riskState !== 'none') {
      badges.push(`<span class="badge risk-${escapeHtml(item.riskState)}">${escapeHtml(item.riskState)}</span>`);
    }
    
    // FP-021: Overdue state (due date passed)
    const now = new Date();
    const dueDate = item.dueDate ? new Date(item.dueDate) : null;
    const isOverdue = dueDate && dueDate < now && item.status !== 'done';
    const isDueSoon = dueDate && !isOverdue && (dueDate - now) <= 7 * 24 * 60 * 60 * 1000 && item.status !== 'done';
    
    if (isOverdue) {
      badges.push(`<span class="badge overdue">overdue</span>`);
      stateClasses.push('item-overdue');
    } else if (isDueSoon) {
      badges.push(`<span class="badge due-soon">due soon</span>`);
      stateClasses.push('item-due-soon');
    }
    
    // FP-023: Stale detection (5 working days = ~7 calendar days)
    const updatedAt = item.updatedAt ? new Date(item.updatedAt) : null;
    const daysSinceUpdate = updatedAt ? (now - updatedAt) / (1000 * 60 * 60 * 24) : 999;
    const isStale = daysSinceUpdate > 7 && item.status !== 'done';
    
    if (isStale) {
      stateClasses.push('item-stale');
    }
    
    // FP-041: Timestamp on Recently changed
    const timestamp = updatedAt ? formatRelativeTime(updatedAt) : '';
    
    return `
    <div class="mini-item ${stateClasses.join(' ')}">
      <div class="mini-title">${escapeHtml(item.title)}</div>
      <div class="mini-sub">${escapeHtml(item.projectName || 'Unknown project')}${timestamp ? ` · ${timestamp}` : ''}</div>
      ${badges.length ? `<div class="mini-meta">${badges.join('')}</div>` : ''}
    </div>
  `}).join('');
}

function formatRelativeTime(date) {
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
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

function visibleProjects() {
  return state.projects
    .filter(project => project.status !== 'cancelled')
    .filter(projectMatches);
}

function renderPortfolioProjects() {
  const filteredProjects = visibleProjects();
  const grid = document.getElementById('projectGrid');

  if (!filteredProjects.length) {
    // FP-030: Improved empty-state treatment
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No projects yet</h3>
        <p>Start by adding a project using the form on the left.</p>
        <p class="empty-hint">Projects group related tasks and track progress in one place.</p>
      </div>`;
    return;
  }

  const sections = {};
  for (const project of filteredProjects) {
    const section = portfolioSectionFor(project);
    sections[section] ||= [];
    sections[section].push(project);
  }

  const orderedSections = ['Products & Platforms', 'Privacy & Governance', 'Finance & Operations', 'Concepts & Strategy', 'Other Workstreams'];

  grid.innerHTML = orderedSections
    .filter(section => sections[section]?.length)
    .map(section => `
      <section class="portfolio-section">
        <div class="portfolio-header">
          <h3>${escapeHtml(section)}</h3>
          <span class="portfolio-count">${sections[section].length} project${sections[section].length === 1 ? '' : 's'}</span>
        </div>
        <div class="portfolio-grid">
          ${sections[section].map(project => renderProjectCard(project)).join('')}
        </div>
      </section>
    `).join('');
}

function renderKanban() {
  const grid = document.getElementById('projectGrid');
  const tasks = sortTasks(visibleProjects().flatMap(project =>
    (project.tasks || []).filter(taskMatches).map(task => ({ ...task, projectName: project.name, projectTags: project.tags || [] }))
  ));

  grid.innerHTML = `
    <section class="kanban-board">
      ${KANBAN_COLUMNS.map(column => {
        const items = tasks.filter(task => task.status === column);
        return `
          <div class="kanban-column">
            <div class="kanban-header">
              <h3>${escapeHtml(column)}</h3>
              <span class="kanban-count">${items.length}</span>
            </div>
            <div class="kanban-list">
              ${items.length ? items.map(task => `
                <article class="kanban-card">
                  <div class="kanban-title">${escapeHtml(task.title)}</div>
                  <div class="kanban-project">${escapeHtml(task.projectName || 'Unknown project')}</div>
                  <div class="kanban-meta">
                    <span class="badge priority-${escapeHtml(task.priority || 'medium')}">${escapeHtml(task.priority || 'medium')}</span>
                    ${task.dueDate ? `<span class="badge">due ${escapeHtml(task.dueDate)}</span>` : ''}
                  </div>
                  ${task.notes ? `<div class="kanban-notes">${escapeHtml(task.notes)}</div>` : ''}
                  <div class="kanban-tags">
                    ${(task.tags || []).map(tag => `<span class="badge">#${escapeHtml(tag)}</span>`).join('')}
                    ${collectSourceTags(task).map(tag => `<span class="badge">${escapeHtml(tag)}</span>`).join('')}
                  </div>
                </article>
              `).join('') : `<div class="empty-tasks">No tasks</div>`}
            </div>
          </div>
        `;
      }).join('')}
    </section>
  `;
}

function renderProjectCard(project) {
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
        ${visibleTasks.length ? visibleTasks.map(task => {
          // FP-021/022: Overdue/due-soon detection
          const now = new Date();
          const dueDate = task.dueDate ? new Date(task.dueDate) : null;
          const isOverdue = dueDate && dueDate < now && task.status !== 'done';
          const isDueSoon = dueDate && !isOverdue && (dueDate - now) <= 7 * 24 * 60 * 60 * 1000 && task.status !== 'done';
          const taskClasses = isOverdue ? 'task-item task-overdue' : isDueSoon ? 'task-item task-due-soon' : 'task-item';
          
          return `
          <div class="${taskClasses}">
            <div class="task-top">
              <input class="task-title-input" data-project-id="${project.id}" data-task-id="${task.id}" data-field="title" value="${escapeHtml(task.title || '')}" />
              <div class="quick-actions">
                <button class="quick-btn" data-action="quick-edit" data-project-id="${project.id}" data-task-id="${task.id}" title="Edit">✎</button>
                <button class="quick-btn" data-action="quick-done" data-project-id="${project.id}" data-task-id="${task.id}" title="Mark done">✓</button>
                <button class="quick-btn danger" data-action="delete-task" data-project-id="${project.id}" data-task-id="${task.id}" title="Delete">×</button>
              </div>
            </div>
            <div class="task-edit-grid">
              <label>Status
                <select data-project-id="${project.id}" data-task-id="${task.id}" data-field="status">
                  ${['todo','in-progress','blocked','done'].map(s => `<option value="${s}" ${task.status === s ? 'selected' : ''}>${s}</option>`).join('')}
                </select>
              </label>
              <label>Priority
                <select data-project-id="${project.id}" data-task-id="${task.id}" data-field="priority">
                  ${['low','medium','high','critical'].map(s => `<option value="${s}" ${task.priority === s ? 'selected' : ''}>${s}</option>`).join('')}
                </select>
              </label>
              <label>Risk
                <select data-project-id="${project.id}" data-task-id="${task.id}" data-field="riskState">
                  ${['none','watch','at-risk','critical'].map(s => `<option value="${s}" ${(task.riskState || 'none') === s ? 'selected' : ''}>${s}</option>`).join('')}
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
              ${task.riskState && task.riskState !== 'none' ? `<span class="badge risk-${task.riskState}">${task.riskState}</span>` : ''}
              ${isOverdue ? `<span class="badge overdue">overdue</span>` : isDueSoon ? `<span class="badge due-soon">due soon</span>` : ''}
              ${task.dueDate && !isOverdue && !isDueSoon ? `<span class="badge">due ${task.dueDate}</span>` : ''}
              ${(task.tags || []).map(tag => `<span class="badge">#${escapeHtml(tag)}</span>`).join('')}
              ${(project.tags || []).filter(isSourceTag).map(tag => `<span class="badge">${escapeHtml(tag)}</span>`).join('')}
            </div>
          </div>
        `}).join('') : `<div class="empty-tasks">No tasks match the current filters.</div>`}
      </div>
    </article>
  `;
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

// FP-092: Workspace Rollups
async function loadWorkspaceRollups() {
  try {
    const response = await request('/rollup');
    return response;
  } catch (e) {
    console.error('[Rollup] Error:', e);
    return { workspaces: [], total: {} };
  }
}

// FP-093: Executive Summary Mode
async function renderExecutiveSummary() {
  const projects = state.projects.filter(p => p.status !== 'cancelled');
  const tasks = allTasksWithProject().filter(t => t.projectStatus !== 'cancelled');
  const now = new Date();
  
  // Load workspace rollups
  const rollup = await loadWorkspaceRollups();
  
  // Calculate executive metrics
  const metrics = {
    totalProjects: projects.length,
    totalTasks: tasks.length,
    completed: tasks.filter(t => t.status === 'done').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    blocked: tasks.filter(t => t.status === 'blocked').length,
    atRisk: tasks.filter(t => t.riskState === 'at-risk' || t.riskState === 'critical').length,
    critical: tasks.filter(t => t.priority === 'critical').length,
    overdue: tasks.filter(t => t.dueDate && new Date(t.dueDate) < now).length,
    workspaces: rollup.total?.workspaces || rollup.workspaces?.length || 0,
  };
  
  // Project summaries
  const projectSummaries = projects.map(p => {
    const pTasks = (p.tasks || []).filter(t => t.status !== 'done');
    return {
      name: p.name,
      status: p.status,
      total: (p.tasks || []).length,
      active: pTasks.length,
      blocked: pTasks.filter(t => t.status === 'blocked').length,
      atRisk: pTasks.filter(t => t.riskState === 'at-risk' || t.riskState === 'critical').length,
    };
  }).sort((a, b) => {
    // Sort by blocked/at-risk first
    if (a.blocked !== b.blocked) return b.blocked - a.blocked;
    if (a.atRisk !== b.atRisk) return b.atRisk - a.atRisk;
    return b.active - a.active;
  }).slice(0, 6);
  
  // Highlight items
  const blockedTasks = tasks.filter(t => t.status === 'blocked').slice(0, 5);
  const criticalTasks = tasks.filter(t => t.priority === 'critical' && t.status !== 'done').slice(0, 5);
  const overdueTasks = tasks.filter(t => t.dueDate && new Date(t.dueDate) < now && t.status !== 'done').slice(0, 5);
  
  const grid = document.getElementById('execGrid');
  const highlights = document.getElementById('execHighlights');
  const timestamp = document.getElementById('execTimestamp');
  
  timestamp.textContent = `As of ${now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}`;
  
  // Project cards
  grid.innerHTML = projectSummaries.map(p => `
    <div class="exec-project">
      <div class="exec-project-header">
        <span class="exec-project-name">${escapeHtml(p.name)}</span>
        ${projectStatusBadge(p.status)}
      </div>
      <div class="exec-metrics">
        <div class="exec-metric">
          <div class="exec-metric-value">${p.total}</div>
          <div class="exec-metric-label">Total</div>
        </div>
        <div class="exec-metric">
          <div class="exec-metric-value">${p.active}</div>
          <div class="exec-metric-label">Active</div>
        </div>
        <div class="exec-metric">
          <div class="exec-metric-value ${p.blocked ? 'danger' : ''}">${p.blocked}</div>
          <div class="exec-metric-label">Blocked</div>
        </div>
        <div class="exec-metric">
          <div class="exec-metric-value ${p.atRisk ? 'warning' : ''}">${p.atRisk}</div>
          <div class="exec-metric-label">At Risk</div>
        </div>
      </div>
    </div>
  `).join('');
  
  // Highlights
  highlights.innerHTML = `
    <div class="exec-highlight ${blockedTasks.length ? 'danger' : ''}">
      <div class="exec-highlight-title">Blocked Tasks</div>
      <div class="exec-highlight-count">${metrics.blocked}</div>
      ${blockedTasks.length ? `<div class="exec-highlight-list">${blockedTasks.map(t => escapeHtml(t.title)).slice(0, 3).join('<br>')}</div>` : ''}
    </div>
    <div class="exec-highlight ${criticalTasks.length ? 'danger' : ''}">
      <div class="exec-highlight-title">Critical Priority</div>
      <div class="exec-highlight-count">${metrics.critical}</div>
      ${criticalTasks.length ? `<div class="exec-highlight-list">${criticalTasks.map(t => escapeHtml(t.title)).slice(0, 3).join('<br>')}</div>` : ''}
    </div>
    <div class="exec-highlight ${overdueTasks.length ? 'warning' : ''}">
      <div class="exec-highlight-title">Overdue</div>
      <div class="exec-highlight-count">${metrics.overdue}</div>
      ${overdueTasks.length ? `<div class="exec-highlight-list">${overdueTasks.map(t => escapeHtml(t.title)).slice(0, 3).join('<br>')}</div>` : ''}
    </div>
  `;
  
  // FP-092: Workspaces section
  if (rollup.workspaces && rollup.workspaces.length > 1) {
    const workspacesSection = document.createElement('div');
    workspacesSection.className = 'exec-workspaces';
    workspacesSection.innerHTML = `
      <h3 style="margin: 0 0 12px 0; font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em;">Workspaces (${rollup.workspaces.length})</h3>
      <div class="exec-workspace-grid">
        ${rollup.workspaces.slice(0, 6).map(ws => `
          <div class="exec-workspace-card">
            <div class="exec-workspace-name">${escapeHtml(ws.source)}</div>
            <div class="exec-workspace-stats">
              <span>${ws.projects} proj</span>
              <span>${ws.tasks} tasks</span>
              ${ws.blocked ? `<span class="danger">${ws.blocked} blocked</span>` : ''}
              ${ws.atRisk ? `<span class="warning">${ws.atRisk} at-risk</span>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    `;
    document.getElementById('execHighlights').after(workspacesSection);
  }
}

// View mode toggle
function setupViewModeToggle() {
  const buttons = document.querySelectorAll('.view-mode-btn');
  const executiveSummary = document.getElementById('executiveSummary');
  const insightStrip = document.getElementById('insightStrip');
  const focusNowPanel = document.getElementById('focusNowPanel');
  const mainLayout = document.querySelector('.layout:not(.executive-summary)');
  
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const mode = btn.dataset.mode;
      if (mode === 'executive') {
        executiveSummary.style.display = 'block';
        insightStrip.style.display = 'none';
        focusNowPanel.style.display = 'none';
        mainLayout.style.display = 'none';
        renderExecutiveSummary();
      } else {
        executiveSummary.style.display = 'none';
        insightStrip.style.display = 'grid';
        renderFocusNow();
        mainLayout.style.display = 'grid';
        render();
      }
    });
  });
}

// FP-091: Dependency Visualization
function showDependencyGraph(projectId, taskId) {
  const panel = document.getElementById('dependencyPanel');
  const content = document.getElementById('dependencyContent');
  const task = allTasksWithProject().find(t => t.projectId === projectId && t.id === taskId);
  
  if (!task) return;
  
  const blockedBy = task.blockedBy || [];
  const blocking = task.blocking || [];
  
  if (blockedBy.length === 0 && blocking.length === 0) {
    content.innerHTML = `
      <div class="dependency-empty">
        <p>No dependencies configured for this task.</p>
        <p class="dependency-hint">Add task IDs to "blockedBy" or "blocking" fields to show dependencies.</p>
      </div>
    `;
  } else {
    content.innerHTML = `
      <div class="dependency-section">
        <h4>Blocked By (${blockedBy.length})</h4>
        <div class="dependency-list">
          ${blockedBy.length ? blockedBy.map(id => renderDependencyItem(id, 'blocked-by')).join('') : '<p class="dependency-none">None</p>'}
        </div>
      </div>
      <div class="dependency-section">
        <h4>Blocking (${blocking.length})</h4>
        <div class="dependency-list">
          ${blocking.length ? blocking.map(id => renderDependencyItem(id, 'blocking')).join('') : '<p class="dependency-none">None</p>'}
        </div>
      </div>
    `;
  }
  
  panel.style.display = 'block';
}

function renderDependencyItem(taskId, type) {
  const task = allTasksWithProject().find(t => t.id === taskId || t.id.endsWith(taskId));
  if (!task) {
    return `<div class="dependency-item missing"><span class="dep-id">${escapeHtml(taskId)}</span><span class="dep-status missing">Not found</span></div>`;
  }
  
  const statusClass = task.status === 'done' ? 'done' : task.status === 'blocked' ? 'blocked' : 'active';
  const icon = type === 'blocked-by' ? '⬆️' : '⬇️';
  
  return `
    <div class="dependency-item ${statusClass}" onclick="scrollToTask('${task.projectId}', '${task.id}')">
      <span class="dep-icon">${icon}</span>
      <span class="dep-title">${escapeHtml(task.title)}</span>
      <span class="dep-project">${escapeHtml(task.projectName)}</span>
      <span class="dep-status ${statusClass}">${escapeHtml(task.status)}</span>
    </div>
  `;
}

function closeDependencyPanel() {
  document.getElementById('dependencyPanel').style.display = 'none';
}
