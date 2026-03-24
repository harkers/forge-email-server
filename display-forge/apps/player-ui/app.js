const API = 'http://localhost:8000';
let playlist = [];
let index = 0;
let timer = null;

async function fetchPlaylist() {
  const res = await fetch(`${API}/api/screens/default/playlist`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  playlist = data.campaigns || [];
}

function renderCurrent() {
  if (!playlist.length) {
    document.getElementById('title').textContent = 'No active campaigns';
    document.getElementById('body').textContent = 'The fallback playlist is empty.';
    return;
  }
  const item = playlist[index % playlist.length];
  const screen = document.getElementById('screen');
  screen.classList.remove('loading');
  screen.style.backgroundImage = `url('${item.media?.url || ''}')`;
  document.getElementById('title').textContent = item.title || 'Untitled';
  document.getElementById('body').textContent = item.body || '';
  document.getElementById('templateBadge').textContent = item.template || 'template';
  document.getElementById('durationBadge').textContent = `${item.durationSeconds || 10}s`;

  const duration = Math.max(3, Number(item.durationSeconds || 10)) * 1000;
  index += 1;
  clearTimeout(timer);
  timer = setTimeout(renderCurrent, duration);
}

async function refreshPlaylist() {
  await fetchPlaylist();
  if (index >= playlist.length) index = 0;
}

async function boot() {
  await refreshPlaylist();
  renderCurrent();
  setInterval(refreshPlaylist, 30000);
}

boot().catch(err => {
  document.getElementById('title').textContent = 'Player error';
  document.getElementById('body').textContent = String(err);
});
