const API = 'http://localhost:8000';
let currentCampaigns = [];

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

function toLocalDateTimeInput(value) {
  if (!value) return '';
  const date = new Date(value);
  const pad = n => String(n).padStart(2, '0');
  const yyyy = date.getFullYear();
  const mm = pad(date.getMonth() + 1);
  const dd = pad(date.getDate());
  const hh = pad(date.getHours());
  const mi = pad(date.getMinutes());
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}`;
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

function renderCards(targetId, campaigns, includeControls = false) {
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
        ${includeControls ? `
          <div class="card-actions">
            <button class="small secondary" data-action="edit" data-id="${item.id}">Edit</button>
            <button class="small danger" data-action="delete" data-id="${item.id}">Delete</button>
          </div>
        ` : ''}
      </div>
    </article>
  `).join('');
}

function resetForm() {
  const form = document.getElementById('campaignForm');
  form.reset();
  form.querySelector('[name="campaignId"]').value = '';
  form.querySelector('[name="status"]').value = 'active';
  form.querySelector('[name="template"]').value = 'announcement';
  form.querySelector('[name="priority"]').value = 50;
  form.querySelector('[name="durationSeconds"]').value = 10;
  document.getElementById('formTitle').textContent = 'Create Campaign';
  document.getElementById('submitButton').textContent = 'Create campaign';
  document.getElementById('cancelEditButton').classList.add('hidden');
}

function fillForm(campaign) {
  const form = document.getElementById('campaignForm');
  form.querySelector('[name="campaignId"]').value = campaign.id || '';
  form.querySelector('[name="title"]').value = campaign.title || '';
  form.querySelector('[name="body"]').value = campaign.body || '';
  form.querySelector('[name="status"]').value = campaign.status || 'draft';
  form.querySelector('[name="template"]').value = campaign.template || 'announcement';
  form.querySelector('[name="priority"]').value = campaign.priority ?? 50;
  form.querySelector('[name="durationSeconds"]').value = campaign.durationSeconds ?? 10;
  form.querySelector('[name="activeFrom"]').value = toLocalDateTimeInput(campaign.activeFrom);
  form.querySelector('[name="activeUntil"]').value = toLocalDateTimeInput(campaign.activeUntil);
  form.querySelector('[name="mediaUrl"]').value = campaign.media?.url || '';
  document.getElementById('formTitle').textContent = `Edit Campaign — ${campaign.id}`;
  document.getElementById('submitButton').textContent = 'Save changes';
  document.getElementById('cancelEditButton').classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function refresh() {
  const [summary, health, campaignData, playlist] = await Promise.all([
    fetchJson('/api/dashboard/summary'),
    fetchJson('/api/health'),
    fetchJson('/api/campaigns'),
    fetchJson('/api/screens/default/playlist'),
  ]);
  currentCampaigns = campaignData.campaigns || [];
  renderSummary(summary);
  document.getElementById('health').textContent = JSON.stringify(health, null, 2);
  renderCards('campaignLibrary', currentCampaigns, true);
  renderCards('playlist', playlist.campaigns || [], false);
}

function bindForm() {
  const form = document.getElementById('campaignForm');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const fd = new FormData(form);
    const campaignId = fd.get('campaignId');
    const mediaUrl = fd.get('mediaUrl') || 'https://picsum.photos/1600/900?random=31';
    const payload = {
      title: fd.get('title'),
      body: fd.get('body'),
      status: fd.get('status'),
      template: fd.get('template'),
      priority: Number(fd.get('priority')),
      durationSeconds: Number(fd.get('durationSeconds')),
      activeFrom: toIsoOrNull(fd.get('activeFrom')),
      activeUntil: toIsoOrNull(fd.get('activeUntil')),
      media: { type: 'image', url: mediaUrl },
    };

    if (campaignId) {
      await fetchJson(`/api/campaigns/${campaignId}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
    } else {
      await fetchJson('/api/campaigns', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    }

    resetForm();
    refresh();
  });

  document.getElementById('cancelEditButton').addEventListener('click', () => {
    resetForm();
  });
}

function bindLibraryActions() {
  document.getElementById('campaignLibrary').addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const id = button.dataset.id;
    const action = button.dataset.action;
    const campaign = currentCampaigns.find(c => c.id === id);
    if (!campaign) return;

    if (action === 'edit') {
      fillForm(campaign);
      return;
    }

    if (action === 'delete') {
      const ok = window.confirm(`Delete campaign ${id} (${campaign.title})?`);
      if (!ok) return;
      await fetchJson(`/api/campaigns/${id}`, { method: 'DELETE' });
      if (document.querySelector('[name="campaignId"]').value === id) {
        resetForm();
      }
      refresh();
    }
  });
}

bindForm();
bindLibraryActions();
resetForm();
refresh().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px">Admin UI failed: ${err}</pre>`;
});
