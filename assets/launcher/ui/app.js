// Интерфейс лаунчера. Данные и запуск — в Python (launcher.pyw, класс Api),
// доступны как window.pywebview.api.*; все вызовы асинхронные.
const $ = (sel) => document.querySelector(sel);
const icon = (name) => `<span class="ic" style="--ic:url(icons/${name}.svg)"></span>`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const STATUS_ICON = { ok: 'circle-check', warn: 'triangle-alert', err: 'triangle-alert', run: 'loader-circle' };

let items = [];
let selected = 0;
let api;

// ---------- плитки ----------

function tileHtml(it, i) {
  return `
    <button class="tile${i === selected ? ' selected' : ''}" type="button" data-i="${i}" title="${esc(it.status.title)}">
      <span class="tile-icon">${icon(it.icon)}</span>
      <span class="tile-text">
        <span class="tile-name">${esc(it.name)}</span>
        <span class="tile-sub">${esc(it.sub)}</span>
      </span>
      <span class="dot ${it.status.kind}"></span>
    </button>`;
}

function renderTiles() {
  $('#games').innerHTML = items.map((it, i) => (it.kind === 'game' ? tileHtml(it, i) : '')).join('');
  $('#profiles').innerHTML = items.map((it, i) => (it.kind === 'mc' ? tileHtml(it, i) : '')).join('');
  document.querySelectorAll('.tile').forEach((el) => {
    const i = Number(el.dataset.i);
    el.addEventListener('click', () => select(i));
    el.addEventListener('dblclick', () => launch(i));
  });
}

// Обновляет только статусы — без пересоздания плиток, чтобы не сбивать hover
function updateTiles() {
  document.querySelectorAll('.tile').forEach((el) => {
    const it = items[Number(el.dataset.i)];
    el.querySelector('.dot').className = `dot ${it.status.kind}`;
    el.title = it.status.title;
  });
}

// ---------- правая панель ----------

function detailHtml(it) {
  const s = it.status;
  const canLaunch = s.kind === 'ok' || s.kind === 'warn';
  return `
    <div class="hero">
      <div class="hero-icon">${icon(it.icon)}</div>
      <div>
        <h1>${esc(it.name)}</h1>
        <div class="tagline">${esc(it.tagline)}</div>
        <div class="chips">${it.stack.map((c) => `<span class="chip">${esc(c)}</span>`).join('')}</div>
      </div>
    </div>

    <p class="desc">${esc(it.desc)}</p>

    <div class="block-label">Возможности</div>
    <ul class="features">${it.features.map((f) => `<li>${esc(f)}</li>`).join('')}</ul>

    <div class="hint">${icon(it.hint_icon)}<span>${esc(it.hint)}</span></div>

    <div class="footer">
      <div class="status ${s.kind}">
        ${icon(STATUS_ICON[s.kind])}
        <span class="status-title">${esc(s.title)}</span>
        <span class="status-detail">${esc(s.detail)}</span>
      </div>
      <div class="actions">
        <button class="btn primary" type="button" data-act="launch" ${canLaunch ? '' : 'disabled'}>
          ${icon('play')}${it.kind === 'game' ? 'Играть' : 'Запустить'}
        </button>
        <button class="btn" type="button" data-act="folder">${icon('folder-open')}Папка</button>
        <button class="btn" type="button" data-act="github">${icon('github')}GitHub</button>
        ${it.has_log ? `<button class="btn" type="button" data-act="log">${icon('file-text')}Лог</button>` : ''}
      </div>
    </div>`;
}

function renderDetail({ animate = false } = {}) {
  const box = $('#detail');
  const paint = () => {
    const it = items[selected];
    box.innerHTML = detailHtml(it);
    box.querySelectorAll('[data-act]').forEach((b) => b.addEventListener('click', () => action(b.dataset.act)));
  };
  if (!animate) return paint();
  // Плавная смена: исчезает → меняется содержимое → появляется
  box.classList.add('leaving');
  setTimeout(() => {
    paint();
    requestAnimationFrame(() => box.classList.remove('leaving'));
  }, 140);
}

function select(i) {
  if (i === selected) return;
  selected = i;
  document.querySelectorAll('.tile').forEach((el) => el.classList.toggle('selected', Number(el.dataset.i) === i));
  renderDetail({ animate: true });
}

// ---------- действия ----------

async function launch(i = selected) {
  const res = await api.launch(items[i].key);
  toast(res);
  await refresh();
}

function action(act) {
  const key = items[selected].key;
  if (act === 'launch') return launch();
  if (act === 'folder') return api.open_folder(key);
  if (act === 'github') return api.open_github(key);
  if (act === 'log') return api.open_log(key);
}

// ---------- уведомления ----------

let toastTimer;
function toast({ kind = 'info', title, body, log }) {
  const slot = $('#toastSlot');
  const old = slot.querySelector('.toast');
  if (old) old.remove();
  clearTimeout(toastTimer);

  const el = document.createElement('div');
  el.className = `toast ${kind}${log ? ' clickable' : ''}`;
  el.innerHTML = `${icon(STATUS_ICON[kind] || 'sparkles')}
    <div><div class="toast-title">${esc(title)}</div><div class="toast-body">${esc(body)}</div></div>`;
  if (log) el.addEventListener('click', () => api.open_log(log));
  slot.appendChild(el);
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('show')));

  toastTimer = setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 350);
  }, 6000);
}

// ---------- состояние из Python ----------

async function refresh() {
  const { items: fresh, events } = await api.poll();
  const changed = JSON.stringify(fresh[selected]) !== JSON.stringify(items[selected]);
  items = fresh;
  updateTiles();
  if (changed) renderDetail();
  events.forEach(toast);
}

function bindUi() {
  $('#siteBtn').addEventListener('click', () => api.open_site());
  $('#minBtn').addEventListener('click', () => api.minimize());
  $('#closeBtn').addEventListener('click', () => api.close());

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') select((selected + 1) % items.length);
    else if (e.key === 'ArrowUp') select((selected - 1 + items.length) % items.length);
    else if (e.key === 'Enter') launch();
    else if (e.key === 'Escape') api.close();
    else return;
    e.preventDefault();
  });
  // Это приложение, а не страница: без контекстного меню браузера
  document.addEventListener('contextmenu', (e) => e.preventDefault());
}

window.addEventListener('pywebviewready', async () => {
  api = window.pywebview.api;
  items = await api.state();
  renderTiles();
  renderDetail();
  bindUi();
  setInterval(refresh, 1000);
});
