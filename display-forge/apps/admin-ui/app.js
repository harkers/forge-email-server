const API = 'http://localhost:8000';

async function fetchJson(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderSummary(summary) {
  const el = document.getElementById('summary');
  const entries = [
    ['Campaigns', summary.campaignCount],
    ['Active', summary.activeCampaignCount],
    ['Screens', summary.screenCount],
    ['Feed Errors', summary.feedErrorCount],
  ];
  el.innerHTML = entries.map(([label, value]) => `
    <div class="stat"><strong>${value}</strong><span>${label}</span></div>
  `).join('');
}

function renderPlaylist(data) {
  const el = document.getElementById('playlist');
  el.innerHTML = (data.campaigns || []).map(item => `
    <article class="campaign">
      <img src="${item.media?.url || ''}" alt="" />
      <div class="copy">
        <h3>${item.title}</h3>
        <p>${item.body || ''}</p>
        <span class="tag">${item.template}</span>
        <span class="tag">${item.durationSeconds}s</span>
        <span class="tag">priority ${item.priority}</span>
      </div>
    </article>
  `).join('');
}

async function boot() {
  const [summary, health, playlist] = await Promise.all([
    fetchJson('/api/dashboard/summary'),
    fetchJson('/api/health'),
    fetchJson('/api/screens/default/playlist'),
  ]);
  renderSummary(summary);
  document.getElementById('health').textContent = JSON.stringify(health, null, 2);
  renderPlaylist(playlist);
}

boot().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px">Admin UI failed: ${err}</pre>`;
});
