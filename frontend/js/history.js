// 로그인 체크
if (!localStorage.getItem('access_token')) {
    alert('로그인이 필요합니다.');
    window.location.href = '/login';
}

const API_BASE = '/api/v1';

// ── 유틸 ─────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('access_token');
}

function scoreClass(score, max) {
  const ratio = score / max;
  if (ratio >= 0.7) return 'high';
  if (ratio >= 0.4) return 'mid';
  return 'low';
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── API 호출 ──────────────────────────────────────────────────────────

async function fetchHistory(page, size) {
  const token = getToken();
  const res = await fetch(`${API_BASE}/feedback/history?page=${page}&size=${size}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (res.status === 401) {
    window.location.href = '/login';
    return null;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || '히스토리 조회에 실패했습니다.');
  }
  return await res.json();
}

// ── 렌더링 ────────────────────────────────────────────────────────────

function renderTable(items) {
  const tbody = document.getElementById('history-body');
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center;color:#999;padding:40px;">
          면접 기록이 없습니다
        </td>
      </tr>`;
    return;
  }

  items.forEach(item => {
    const date = new Date(item.created_at).toLocaleDateString('ko-KR', {
      year: 'numeric', month: '2-digit', day: '2-digit'
    });
    const techStack     = (item.tech_stack || []).join(', ') || '-';
    const techScore     = Number(item.technical_score).toFixed(1);
    const logicScore    = Number(item.logic_score).toFixed(1);
    const attitudeScore = Number(item.posture_summary.attitude_score).toFixed(1);
    const avg           = ((item.technical_score + item.logic_score) / 2).toFixed(1);

    const techCls     = scoreClass(item.technical_score, 10);
    const logicCls    = scoreClass(item.logic_score, 10);
    const attitudeCls = scoreClass(item.posture_summary.attitude_score, 10);
    const avgCls      = scoreClass(parseFloat(avg), 10);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${date}</td>
      <td>${escapeHtml(item.position || '-')}</td>
      <td>${escapeHtml(techStack)}</td>
      <td><span class="score-badge ${techCls}">${techScore}</span></td>
      <td><span class="score-badge ${logicCls}">${logicScore}</span></td>
      <td><span class="score-badge ${attitudeCls}">${attitudeScore}</span></td>
      <td><span class="score-badge ${avgCls}">${avg}</span></td>
      <td><a href="/feedback?id=${item.interview_id}" class="btn-detail">상세보기</a></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderPagination(total, page, size) {
  const container = document.getElementById('pagination');
  if (!container) return;

  const totalPages = Math.ceil(total / size);
  if (totalPages <= 1) {
    container.innerHTML = '';
    return;
  }

  let html = '';
  if (page > 1) {
    html += `<button onclick="goPage(${page - 1})">◀</button>`;
  }
  for (let i = 1; i <= totalPages; i++) {
    html += `<button onclick="goPage(${i})" class="${i === page ? 'active' : ''}">${i}</button>`;
  }
  if (page < totalPages) {
    html += `<button onclick="goPage(${page + 1})">▶</button>`;
  }
  container.innerHTML = html;
}

// ── 페이지 이동 ───────────────────────────────────────────────────────

const PAGE_SIZE = 10;

async function goPage(page) {
  await load(page);
}

async function load(page) {
  try {
    const data = await fetchHistory(page, PAGE_SIZE);
    if (!data) return;
    renderTable(data.items);
    renderPagination(data.total, data.page, PAGE_SIZE);
  } catch (e) {
    document.getElementById('history-body').innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center;color:#c62828;padding:40px;">
          ${escapeHtml(e.message)}
        </td>
      </tr>`;
  }
}

// ── 진입점 ────────────────────────────────────────────────────────────

(async function init() {
  const token = getToken();
  if (!token) {
    window.location.href = '/login';
    return;
  }
  await load(1);
})();
