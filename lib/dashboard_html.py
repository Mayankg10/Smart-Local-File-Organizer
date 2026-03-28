"""Dashboard HTML template (CSS + HTML + JS)."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>File Organizer Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg-primary: #09090b;
    --bg-secondary: #0f0f12;
    --bg-card: #141418;
    --bg-card-hover: #1c1c22;
    --border: #27272a;
    --border-light: #3f3f46;
    --accent: #a78bfa;
    --accent-dim: #7c3aed;
    --accent-glow: rgba(167, 139, 250, 0.1);
    --accent-glow-strong: rgba(167, 139, 250, 0.2);
    --success: #34d399;
    --blue: #60a5fa;
    --yellow: #fbbf24;
    --red: #f87171;
    --text-primary: #fafafa;
    --text-secondary: #a1a1aa;
    --text-dim: #52525b;
    --font: -apple-system, 'Inter', 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
    --font-mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', monospace;
  }

  body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font);
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* ─── Header ─── */
  .header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .logo {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--blue));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }

  .header h1 {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.5px;
  }

  .header h1 span { color: var(--text-primary); font-weight: 400; }

  .status {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    background: var(--success);
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* ─── Layout ─── */
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 32px;
  }

  /* ─── Stat Cards Row ─── */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }

  .stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s;
  }

  .stat-card:hover {
    border-color: var(--border-light);
    background: var(--bg-card-hover);
  }

  .stat-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--text-dim);
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    font-family: var(--font-mono);
  }

  .stat-sub {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 6px;
  }

  /* ─── Grid Layout ─── */
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }

  .grid-full {
    grid-column: 1 / -1;
  }

  /* ─── Cards ─── */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .card-title {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary);
  }

  .card-body { padding: 20px; }

  /* ─── Category Bars ─── */
  .cat-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .cat-row:last-child { margin-bottom: 0; }

  .cat-name {
    width: 120px;
    font-size: 13px;
    color: var(--text-secondary);
    text-align: right;
    flex-shrink: 0;
  }

  .cat-bar-bg {
    flex: 1;
    height: 24px;
    background: var(--bg-primary);
    border-radius: 6px;
    overflow: hidden;
    position: relative;
  }

  .cat-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--blue));
    border-radius: 6px;
    transition: width 0.8s ease;
    min-width: 2px;
    opacity: 0.85;
  }

  .cat-count {
    width: 50px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    text-align: right;
    flex-shrink: 0;
  }

  /* ─── Timeline ─── */
  .timeline-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    gap: 16px;
  }

  .timeline-row:last-child { border-bottom: none; }

  .timeline-date {
    font-size: 12px;
    color: var(--text-dim);
    width: 140px;
    flex-shrink: 0;
  }

  .timeline-bar-bg {
    flex: 1;
    height: 8px;
    background: var(--bg-primary);
    border-radius: 4px;
    overflow: hidden;
  }

  .timeline-bar {
    height: 100%;
    background: var(--accent);
    border-radius: 4px;
    opacity: 0.8;
  }

  .timeline-count {
    font-size: 12px;
    color: var(--text-secondary);
    width: 60px;
    text-align: right;
    flex-shrink: 0;
  }

  .timeline-target {
    font-size: 11px;
    color: var(--text-dim);
    width: 120px;
    text-align: right;
    flex-shrink: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* ─── Recent Operations ─── */
  .op-card {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.2s;
  }

  .op-card:hover {
    border-color: var(--border-light);
    background: var(--bg-card);
  }

  .op-card:last-child { margin-bottom: 0; }

  .op-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .op-time {
    font-size: 12px;
    color: var(--text-dim);
  }

  .op-count {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    font-family: var(--font-mono);
  }

  .op-target {
    font-size: 11px;
    color: var(--text-dim);
    margin-bottom: 6px;
  }

  .op-files {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .op-file {
    font-size: 11px;
    background: rgba(167, 139, 250, 0.06);
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 4px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
  }

  /* ─── Logs ─── */
  .log-entry {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 10px;
    overflow: hidden;
  }

  .log-header {
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: background 0.2s;
  }

  .log-header:hover { background: var(--bg-card-hover); }

  .log-date {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .log-size {
    font-size: 11px;
    color: var(--text-dim);
  }

  .log-content {
    display: none;
    padding: 14px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    line-height: 1.7;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 400px;
    overflow-y: auto;
  }

  .log-content.open { display: block; }

  /* ─── Empty State ─── */
  .empty {
    text-align: center;
    padding: 40px;
    color: var(--text-dim);
  }

  .empty-icon {
    font-size: 32px;
    margin-bottom: 12px;
  }

  /* ─── Monthly Chart ─── */
  .month-chart {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 120px;
    padding-top: 10px;
  }

  .month-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    height: 100%;
    justify-content: flex-end;
  }

  .month-bar {
    width: 100%;
    background: linear-gradient(180deg, var(--blue), rgba(96, 165, 250, 0.2));
    border-radius: 4px 4px 0 0;
    min-height: 2px;
    transition: height 0.8s ease;
  }

  .month-label {
    font-size: 10px;
    color: var(--text-dim);
    white-space: nowrap;
  }

  .month-value {
    font-size: 10px;
    color: var(--text-secondary);
    font-weight: 600;
  }

  /* ─── Tabs ─── */
  .tabs {
    display: flex;
    gap: 2px;
    margin-bottom: 24px;
    background: var(--bg-secondary);
    border-radius: 10px;
    padding: 3px;
    border: 1px solid var(--border);
    width: fit-content;
  }

  .tab {
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-dim);
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.2s;
    border: none;
    background: none;
    font-family: var(--font);
  }

  .tab:hover { color: var(--text-secondary); }

  .tab.active {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);
  }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* ─── Reclaim ─── */
  .reclaim-section {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
  }

  .reclaim-section.empty-section { opacity: 0.5; }

  .reclaim-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .reclaim-title {
    font-size: 15px;
    font-weight: 600;
  }

  .reclaim-meta {
    font-size: 13px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
  }

  .reclaim-files {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 14px;
  }

  .reclaim-file {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    background: var(--bg-card);
    border-radius: 6px;
    font-size: 13px;
  }

  .reclaim-file-name {
    color: var(--text-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    font-family: var(--font-mono);
    font-size: 12px;
  }

  .reclaim-file-size {
    color: var(--text-dim);
    font-size: 12px;
    margin-left: 12px;
    flex-shrink: 0;
    font-family: var(--font-mono);
  }

  .reclaim-file .dup-tag {
    font-size: 10px;
    padding: 1px 6px;
    border-radius: 3px;
    margin-left: 8px;
    flex-shrink: 0;
  }

  .dup-tag.original { background: rgba(52,211,153,0.15); color: var(--success); }
  .dup-tag.duplicate { background: rgba(248,113,113,0.15); color: var(--red); }

  .btn {
    padding: 8px 18px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-primary);
    font-family: var(--font);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-light);
  }

  .btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .btn-danger {
    border-color: rgba(248,113,113,0.3);
    color: var(--red);
  }

  .btn-danger:hover {
    background: rgba(248,113,113,0.1);
    border-color: var(--red);
  }

  .btn-scan {
    border-color: rgba(167,139,250,0.3);
    color: var(--accent);
  }

  .btn-scan:hover {
    background: rgba(167,139,250,0.1);
    border-color: var(--accent);
  }

  .reclaim-summary {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .reclaim-total {
    font-size: 28px;
    font-weight: 700;
    font-family: var(--font-mono);
  }

  .reclaim-total-label {
    font-size: 12px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .reclaim-actions {
    display: flex;
    gap: 10px;
  }

  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--bg-card);
    border: 1px solid var(--success);
    border-radius: 10px;
    padding: 14px 20px;
    color: var(--success);
    font-size: 14px;
    font-weight: 500;
    z-index: 1000;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s;
    pointer-events: none;
  }

  .toast.show {
    opacity: 1;
    transform: translateY(0);
  }

  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid var(--border-light);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* ─── Scrollbar ─── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg-primary); }
  ::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
  }

  /* ─── Responsive ─── */
  @media (max-width: 900px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .grid { grid-template-columns: 1fr; }
    .container { padding: 16px; }
    .header { padding: 16px; }
  }
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="logo">📂</div>
    <h1>File <span>Organizer</span> Dashboard</h1>
  </div>
  <div class="status">
    <div class="status-dot"></div>
    <span id="last-updated">Loading...</span>
  </div>
</div>

<div class="container">

  <!-- Action Bar -->
  <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap">
    <button class="btn btn-scan" id="btn-run-now" onclick="runOrganizeNow()">▶ Run Now</button>
    <button class="btn" id="btn-undo" onclick="runUndo(false)">↩ Undo Last</button>
    <button class="btn btn-danger" id="btn-undo-all" onclick="runUndo(true)">↩ Undo All</button>
  </div>

  <!-- Stat Cards -->
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-label">Total Operations</div>
      <div class="stat-value" id="stat-ops">—</div>
      <div class="stat-sub" id="stat-ops-sub"></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Files Organized</div>
      <div class="stat-value" id="stat-files">—</div>
      <div class="stat-sub" id="stat-files-sub"></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Categories</div>
      <div class="stat-value" id="stat-cats">—</div>
      <div class="stat-sub">unique file types</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Directories</div>
      <div class="stat-value" id="stat-dirs">—</div>
      <div class="stat-sub" id="stat-dirs-sub"></div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('overview')">Overview</button>
    <button class="tab" onclick="switchTab('reclaim')">Reclaim</button>
    <button class="tab" onclick="switchTab('history')">History</button>
    <button class="tab" onclick="switchTab('logs')">Logs</button>
  </div>

  <!-- Overview Tab -->
  <div class="tab-content active" id="tab-overview">
    <div class="grid">
      <!-- Category Breakdown -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">📊 Category Breakdown</span>
        </div>
        <div class="card-body" id="category-chart"></div>
      </div>

      <!-- Monthly Activity -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">📅 Monthly Activity</span>
        </div>
        <div class="card-body" id="monthly-chart"></div>
      </div>

      <!-- Recent Activity -->
      <div class="card grid-full">
        <div class="card-header">
          <span class="card-title">⚡ Recent Operations</span>
        </div>
        <div class="card-body" id="recent-ops"></div>
      </div>
    </div>
  </div>

  <!-- Reclaim Tab -->
  <div class="tab-content" id="tab-reclaim">
    <div class="reclaim-summary" id="reclaim-summary">
      <div>
        <div class="reclaim-total-label">Reclaimable Space</div>
        <div class="reclaim-total" id="reclaim-total">—</div>
        <div style="font-size:12px;color:var(--text-dim);margin-top:4px" id="reclaim-total-sub"></div>
      </div>
      <div class="reclaim-actions">
        <button class="btn btn-scan" onclick="scanReclaim()" id="btn-scan">Scan Now</button>
      </div>
    </div>
    <div id="reclaim-content">
      <div class="empty"><div class="empty-icon">💾</div>Click "Scan Now" to analyze your Downloads & Desktop.</div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <!-- History Tab -->
  <div class="tab-content" id="tab-history">
    <div class="card" style="margin-bottom:16px">
      <div class="card-header">
        <span class="card-title">🕐 Organize Timeline</span>
      </div>
      <div class="card-body" id="timeline"></div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">🗑 Reclaim History</span>
        <span id="reclaim-history-total" style="font-size:12px;color:var(--text-dim);font-family:var(--font-mono)"></span>
      </div>
      <div class="card-body" id="reclaim-timeline"></div>
    </div>
  </div>

  <!-- Logs Tab -->
  <div class="tab-content" id="tab-logs">
    <div class="card">
      <div class="card-header">
        <span class="card-title">📜 Auto-Organize Logs</span>
      </div>
      <div class="card-body" id="logs-list"></div>
    </div>
  </div>

</div>

<script>
  function switchTab(name) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
  }

  function toggleLog(el) {
    const content = el.nextElementSibling;
    content.classList.toggle('open');
  }

  function shortPath(p) {
    return p.replace(/^\\/Users\\/[^\\/]+/, '~');
  }

  function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }

  function humanSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++; }
    return bytes.toFixed(1) + ' ' + units[i];
  }

  function humanAge(seconds) {
    const days = seconds / 86400;
    if (days < 1) return Math.round(seconds / 3600) + 'h';
    if (days < 30) return Math.round(days) + 'd';
    if (days < 365) return Math.round(days / 30) + 'mo';
    return (days / 365).toFixed(1) + 'y';
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3500);
  }

  // --- Run Now & Undo ---
  async function runOrganizeNow() {
    const btn = document.getElementById('btn-run-now');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Organizing...';
    try {
      const res = await fetch('/api/organize', {method: 'POST'});
      const result = await res.json();
      showToast('✓ ' + result.message);
      loadData();
    } catch (e) {
      showToast('Failed to run organizer');
    }
    btn.disabled = false;
    btn.innerHTML = '▶ Run Now';
  }

  async function runUndo(all) {
    const label = all ? 'ALL operations' : 'the last operation';
    if (!confirm('Undo ' + label + '? Files will be moved back to their original locations.')) return;
    const btn = all ? document.getElementById('btn-undo-all') : document.getElementById('btn-undo');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Undoing...';
    try {
      const res = await fetch('/api/undo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({all: all}),
      });
      const result = await res.json();
      showToast('✓ ' + result.message);
      loadData();
    } catch (e) {
      showToast('Undo failed');
    }
    btn.disabled = false;
    btn.innerHTML = all ? '↩ Undo All' : '↩ Undo Last';
  }

  let reclaimData = null;

  async function scanReclaim() {
    const btn = document.getElementById('btn-scan');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Scanning...';

    try {
      const res = await fetch('/api/reclaim/scan');
      reclaimData = await res.json();
      renderReclaim(reclaimData);
    } catch (e) {
      console.error(e);
      showToast('Scan failed');
    }

    btn.disabled = false;
    btn.textContent = 'Scan Now';
  }

  async function deleteCategory(category) {
    if (!reclaimData) return;
    let paths = [];
    let label = '';
    if (category === 'junk') {
      paths = reclaimData.junk.map(f => f.path);
      label = 'junk files';
    } else if (category === 'duplicates') {
      paths = reclaimData.duplicates.map(f => f.path);
      label = 'duplicates';
    } else if (category === 'stale') {
      paths = reclaimData.stale.map(f => f.path);
      label = 'stale files';
    }
    if (paths.length === 0) return;
    if (!confirm('Delete ' + paths.length + ' ' + label + '? This cannot be undone.')) return;

    try {
      const res = await fetch('/api/reclaim/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({paths, category}),
      });
      const result = await res.json();
      showToast('✓ Deleted ' + result.deleted + ' files, freed ' + humanSize(result.freed));
      scanReclaim();
      loadData();
    } catch (e) {
      showToast('Delete failed');
    }
  }

  function renderReclaim(data) {
    document.getElementById('reclaim-total').textContent = humanSize(data.total_reclaimable);
    document.getElementById('reclaim-total-sub').textContent =
      humanSize(data.total_with_stale) + ' total if stale files included';

    let html = '';

    // Junk
    html += `<div class="reclaim-section ${data.junk.length === 0 ? 'empty-section' : ''}">`;
    html += `<div class="reclaim-header">
      <span class="reclaim-title">🗑 Junk & Temp Files</span>
      <span class="reclaim-meta">${data.junk.length} files · ${humanSize(data.junk_size)}</span>
    </div>`;
    if (data.junk.length > 0) {
      html += '<div class="reclaim-files">';
      data.junk.slice(0, 8).forEach(f => {
        html += `<div class="reclaim-file">
          <span class="reclaim-file-name">${f.name}</span>
          <span class="reclaim-file-size">${f.size === 0 ? 'empty' : humanSize(f.size)}</span>
        </div>`;
      });
      if (data.junk.length > 8) html += `<div style="font-size:12px;color:var(--text-dim);padding:4px 10px">... and ${data.junk.length - 8} more</div>`;
      html += '</div>';
      html += `<button class="btn btn-danger" onclick="deleteCategory('junk')">Delete ${data.junk.length} junk files</button>`;
    } else {
      html += '<div style="color:var(--text-dim);font-size:13px">✓ No junk files found</div>';
    }
    html += '</div>';

    // Duplicates
    html += `<div class="reclaim-section ${data.duplicates.length === 0 ? 'empty-section' : ''}">`;
    html += `<div class="reclaim-header">
      <span class="reclaim-title">🔍 Duplicate Files</span>
      <span class="reclaim-meta">${data.duplicates.length} duplicates in ${data.dup_groups.length} groups · ${humanSize(data.dup_size)}</span>
    </div>`;
    if (data.dup_groups.length > 0) {
      html += '<div class="reclaim-files">';
      data.dup_groups.slice(0, 5).forEach(group => {
        group.forEach(f => {
          const tag = f.is_original
            ? '<span class="dup-tag original">keep</span>'
            : '<span class="dup-tag duplicate">duplicate</span>';
          html += `<div class="reclaim-file">
            <span class="reclaim-file-name">${f.name}</span>
            ${tag}
            <span class="reclaim-file-size">${humanSize(f.size)}</span>
          </div>`;
        });
      });
      if (data.dup_groups.length > 5) html += `<div style="font-size:12px;color:var(--text-dim);padding:4px 10px">... and ${data.dup_groups.length - 5} more groups</div>`;
      html += '</div>';
      html += `<button class="btn btn-danger" onclick="deleteCategory('duplicates')">Delete ${data.duplicates.length} duplicates</button>`;
    } else {
      html += '<div style="color:var(--text-dim);font-size:13px">✓ No duplicates found</div>';
    }
    html += '</div>';

    // Stale
    html += `<div class="reclaim-section ${data.stale.length === 0 ? 'empty-section' : ''}">`;
    html += `<div class="reclaim-header">
      <span class="reclaim-title">🕸 Stale Files (90+ days)</span>
      <span class="reclaim-meta">${data.stale.length} files · ${humanSize(data.stale_size)}</span>
    </div>`;
    if (data.stale.length > 0) {
      html += '<div class="reclaim-files">';
      data.stale.slice(0, 8).forEach(f => {
        html += `<div class="reclaim-file">
          <span class="reclaim-file-name">${f.name}</span>
          <span class="reclaim-file-size">${humanSize(f.size)} · ${humanAge(f.age)} ago</span>
        </div>`;
      });
      if (data.stale.length > 8) html += `<div style="font-size:12px;color:var(--text-dim);padding:4px 10px">... and ${data.stale.length - 8} more</div>`;
      html += '</div>';
      html += `<button class="btn btn-danger" onclick="deleteCategory('stale')">Delete ${data.stale.length} stale files</button>`;
    } else {
      html += '<div style="color:var(--text-dim);font-size:13px">✓ No stale files found</div>';
    }
    html += '</div>';

    document.getElementById('reclaim-content').innerHTML = html;
  }

  async function loadData() {
    try {
      const [statsRes, logsRes] = await Promise.all([
        fetch('/api/stats'),
        fetch('/api/logs'),
      ]);
      const stats = await statsRes.json();
      const logs = await logsRes.json();
      render(stats, logs);
      document.getElementById('last-updated').textContent =
        'Updated ' + new Date().toLocaleTimeString();
    } catch (e) {
      console.error('Failed to load:', e);
    }
  }

  function render(stats, logs) {
    // Stat cards
    document.getElementById('stat-ops').textContent = stats.total_operations;
    document.getElementById('stat-files').textContent = stats.total_files_moved.toLocaleString();
    document.getElementById('stat-cats').textContent = Object.keys(stats.categories).length;
    document.getElementById('stat-dirs').textContent = Object.keys(stats.by_directory).length;

    const dirNames = Object.keys(stats.by_directory).map(shortPath);
    document.getElementById('stat-dirs-sub').textContent = dirNames.join(', ') || '—';

    if (stats.total_operations > 0) {
      const avg = Math.round(stats.total_files_moved / stats.total_operations);
      document.getElementById('stat-ops-sub').textContent = avg + ' files avg per run';
      document.getElementById('stat-files-sub').textContent = 'across all operations';
    }

    // Category chart
    const catEl = document.getElementById('category-chart');
    const cats = stats.categories;
    const maxCat = Math.max(...Object.values(cats), 1);

    if (Object.keys(cats).length === 0) {
      catEl.innerHTML = '<div class="empty"><div class="empty-icon">📭</div>No data yet.<br>Run the organizer to see stats here.</div>';
    } else {
      catEl.innerHTML = Object.entries(cats).map(([name, count]) => {
        const pct = (count / maxCat * 100).toFixed(1);
        return `<div class="cat-row">
          <span class="cat-name">${name}</span>
          <div class="cat-bar-bg"><div class="cat-bar" style="width:${pct}%"></div></div>
          <span class="cat-count">${count}</span>
        </div>`;
      }).join('');
    }

    // Monthly chart
    const monthEl = document.getElementById('monthly-chart');
    const months = stats.by_month;
    const maxMonth = Math.max(...Object.values(months), 1);

    if (Object.keys(months).length === 0) {
      monthEl.innerHTML = '<div class="empty"><div class="empty-icon">📅</div>No monthly data yet.</div>';
    } else {
      monthEl.innerHTML = '<div class="month-chart">' +
        Object.entries(months).map(([month, count]) => {
          const pct = (count / maxMonth * 100).toFixed(1);
          return `<div class="month-col">
            <span class="month-value">${count}</span>
            <div class="month-bar" style="height:${pct}%"></div>
            <span class="month-label">${month.slice(2)}</span>
          </div>`;
        }).join('') + '</div>';
    }

    // Recent operations
    const recentEl = document.getElementById('recent-ops');
    const recent = stats.recent_operations;

    if (recent.length === 0) {
      recentEl.innerHTML = '<div class="empty"><div class="empty-icon">⚡</div>No operations yet.</div>';
    } else {
      recentEl.innerHTML = recent.map(op => `
        <div class="op-card">
          <div class="op-top">
            <span class="op-time">${formatDate(op.timestamp)}</span>
            <span class="op-count">${op.files_moved} files</span>
          </div>
          <div class="op-target">${shortPath(op.target_dir)}</div>
          <div class="op-files">
            ${op.sample_files.map(f => `<span class="op-file">${f}</span>`).join('')}
            ${op.files_moved > 5 ? `<span class="op-file">+${op.files_moved - 5} more</span>` : ''}
          </div>
        </div>
      `).join('');
    }

    // Timeline
    const timelineEl = document.getElementById('timeline');
    const tl = stats.timeline;

    if (tl.length === 0) {
      timelineEl.innerHTML = '<div class="empty"><div class="empty-icon">🕐</div>No history yet.</div>';
    } else {
      const maxTl = Math.max(...tl.map(t => t.count), 1);
      timelineEl.innerHTML = [...tl].reverse().map(t => {
        const pct = (t.count / maxTl * 100).toFixed(1);
        return `<div class="timeline-row">
          <span class="timeline-date">${t.date}</span>
          <div class="timeline-bar-bg"><div class="timeline-bar" style="width:${pct}%"></div></div>
          <span class="timeline-count">${t.count} files</span>
          <span class="timeline-target">${shortPath(t.target)}</span>
        </div>`;
      }).join('');
    }

    // Reclaim history
    const reclaimEl = document.getElementById('reclaim-timeline');
    const rh = stats.reclaim_history || [];
    const totalReclaimed = stats.total_reclaimed || 0;

    document.getElementById('reclaim-history-total').textContent =
      totalReclaimed > 0 ? humanSize(totalReclaimed) + ' total reclaimed' : '';

    if (rh.length === 0) {
      reclaimEl.innerHTML = '<div class="empty"><div class="empty-icon">🗑</div>No reclaim operations yet.<br>Use the Reclaim tab to free up space.</div>';
    } else {
      const catIcons = {junk: '🗑', duplicates: '🔍', stale: '🕸', unknown: '📁'};
      const catColors = {junk: 'var(--red)', duplicates: 'var(--accent)', stale: 'var(--yellow)', unknown: 'var(--text-dim)'};
      reclaimEl.innerHTML = rh.map(r => {
        const icon = catIcons[r.category] || '📁';
        const color = catColors[r.category] || 'var(--text-dim)';
        const ts = formatDate(r.timestamp);
        const files = (r.sample_files || []).slice(0, 4);
        return `<div class="op-card">
          <div class="op-top">
            <span class="op-time">${ts}</span>
            <span class="op-count" style="color:${color}">${icon} ${r.deleted} ${r.category}</span>
          </div>
          <div style="font-size:13px;font-family:var(--font-mono);color:var(--text-secondary);margin-bottom:6px">
            ${humanSize(r.freed)} freed
          </div>
          <div class="op-files">
            ${files.map(f => `<span class="op-file">${f}</span>`).join('')}
            ${r.deleted > 4 ? `<span class="op-file">+${r.deleted - 4} more</span>` : ''}
          </div>
        </div>`;
      }).join('');
    }

    // Logs
    const logsEl = document.getElementById('logs-list');
    if (logs.length === 0) {
      logsEl.innerHTML = '<div class="empty"><div class="empty-icon">📜</div>No logs yet.<br>Logs are created by the weekly auto-organizer.</div>';
    } else {
      logsEl.innerHTML = logs.map(log => `
        <div class="log-entry">
          <div class="log-header" onclick="toggleLog(this)">
            <span class="log-date">📄 ${log.date}</span>
            <span class="log-size">${humanSize(log.size)}</span>
          </div>
          <div class="log-content">${log.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        </div>
      `).join('');
    }
  }

  // Initial load + auto-refresh every 30s
  loadData();
  setInterval(loadData, 30000);
</script>

</body>
</html>"""
