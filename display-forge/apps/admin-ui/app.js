const API = 'http://localhost:8000';

async function fetchJson(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  if (res.status === 204) return null;
  return res.json();
}

function toIsoOrNull(value) {
  if (!value) return null;
  return new Date(value).toISOString();
}

function renderSummary(summary) {
  const el = document.getElementById('summary');
  const entries = [
    ['Campaigns', summary.campaignCount],
    ['Active now', summary.activeCampaignCount],
    ['Scheduled', summary.scheduledCampaignCount],
    ['Expired', summary.expiredCampaignCount],
    ['Screens', summary.screenCount],
    ['Feed Errors', summary.feedErrorCount],
  ];
  el.innerHTML = entries.map(([label, value]) => `
    <div class="stat"><strong>${value}</strong><span>${label}</span></div>
  `).join('');
}

function renderCards(targetId, campaigns) {
  const el = document.getElementById(targetId);
  el.innerHTML = campaigns.map(item => `
    <article class="campaign">
      <img src="${item.media?.url || ''}" alt="" />
      <div class="copy">
        <h3>${item.title}</h3>
        <p>${item.body || ''}</p>
        <span class="tag">${item.status}</span>
        <span class="tag">${item.template}</span>
        <span class="tag">${item.durationSeconds}s</span>
        <span class="tag">priority ${item.priority}</span>
        ${item.eligibility ? `<span class="tag state">${item.eligibility}</span>` : ''}
        ${item.activeFrom ? `<div class="schedule">from ${item.activeFrom}</div>` : ''}
        ${item.activeUntil ? `<div class="schedule">until ${item.activeUntil}</div>` : ''}
      </div>
    </article>
  `).join('');
}

async function refresh() {
  const [summary, health, campaignData, playlist] = await Promise.all([
    fetchJson('/api/dashboard/summary'),
    fetchJson('/api/health'),
    fetchJson('/api/campaigns'),
    fetchJson('/api/screens/default/playlist'),
  ]);
  renderSummary(summary);
  document.getElementById('health').textContent = JSON.stringify(health, null, 2);
  renderCards('campaignLibrary', campaignData.campaigns || []);
  renderCards('playlist', playlist.campaigns || []);
}

function bindForm() {
  const form = document.getElementById('campaignForm');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const fd = new FormData(form);
    const mediaUrl = fd.get('mediaUrl') || 'https://picsum.photos/1600/900?random=31';
    await fetchJson('/api/campaigns', {
      method: 'POST',
      body: JSON.stringify({
        title: fd.get('title'),
        body: fd.get('body'),
        status: fd.get('status'),
        template: fd.get('template'),
        priority: Number(fd.get('priority')),
        durationSeconds: Number(fd.get('durationSeconds')),
        activeFrom: toIsoOrNull(fd.get('activeFrom')),
        activeUntil: toIsoOrNull(fd.get('activeUntil')),
        media: { type: 'image', url: mediaUrl },
      }),
    });
    form.reset();
    form.querySelector('[name="status"]').value = 'active';
    form.querySelector('[name="template"]').value = 'announcement';
    form.querySelector('[name="priority"]').value = 50;
    form.querySelector('[name="durationSeconds"]').value = 10;
    refresh();
  });
}

bindForm();
refresh().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px">Admin UI failed: ${err}</pre>`;
});
