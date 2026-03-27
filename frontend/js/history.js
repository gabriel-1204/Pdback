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
        <td colspan="6" style="text-align:center;color:#999;padding:40px;">
          면접 기록이 없습니다
        </td>
      </tr>`;
    return;
  }

  items.forEach(item => {
    const date         = new Date(item.created_at).toLocaleDateString('ko-KR', {
      year: 'numeric', month: '2-digit', day: '2-digit'
    });
    const techStack    = (item.tech_stack || []).join(', ') || '-';
    const overallScore = Number(item.interview_score).toFixed(1);
    const attitudeScore = Number(item.posture_summary.attitude_score).toFixed(1);

    const overallCls  = scoreClass(item.interview_score, 10);
    const attitudeCls = scoreClass(item.posture_summary.attitude_score, 10);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${date}</td>
      <td>${escapeHtml(item.position || '-')}</td>
      <td>${escapeHtml(techStack)}</td>
      <td><span class="score-badge ${overallCls}">${overallScore}</span></td>
      <td><span class="score-badge ${attitudeCls}">${attitudeScore}</span></td>
      <td><a href="/feedback?id=${item.interview_id}" class="btn-detail">상세보기</a></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderTrendChart(items) {
  const container = document.getElementById('trend-chart');
  if (!items || items.length === 0) {
    container.textContent = '면접 기록이 없습니다';
    return;
  }

  // 최신 5개만 자르고, 차트는 오래된 순(왼쪽→오른쪽)으로 뒤집기
  const CHART_LIMIT = 5;
  const sorted = [...items].slice(0, CHART_LIMIT).reverse();

  const W = 600, H = 140;
  const PAD = { top: 20, right: 20, bottom: 30, left: 30 };
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const n = sorted.length;

  const points = sorted.map((item, i) => {
    const x = PAD.left + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW);
    const y = PAD.top + innerH - (item.interview_score / 10) * innerH;
    return { x, y, score: item.interview_score, date: item.created_at };
  });

  const polyline = points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');

  const circles = points.map(p => `
    <circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="4" fill="#4A6CF7"/>
    <text x="${p.x.toFixed(1)}" y="${(p.y - 8).toFixed(1)}" text-anchor="middle" font-size="11" fill="#444">${Number(p.score).toFixed(1)}</text>
  `).join('');

  const step = Math.max(1, Math.ceil(n / 5));
  const xLabels = points
    .filter((_, i) => i % step === 0 || i === n - 1)
    .map(p => {
      const d = new Date(p.date).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' });
      return `<text x="${p.x.toFixed(1)}" y="${H - 4}" text-anchor="middle" font-size="10" fill="#aaa">${d}</text>`;
    }).join('');

  container.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:100%;">
      <polyline points="${polyline}" fill="none" stroke="#4A6CF7" stroke-width="2"/>
      ${circles}
      ${xLabels}
      <text x="${W - PAD.right}" y="${PAD.top - 6}" text-anchor="end" font-size="10" fill="#bbb">최근 ${sorted.length}개 면접 기준</text>
    </svg>
  `;
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

// ── 페이지 상태 ───────────────────────────────────────────────────────

const PAGE_SIZE = 10;
let currentPage = 1;  // 지금 보고 있는 페이지 번호
let totalPages = 0;   // 전체 페이지 수

// ── 페이지 이동 ───────────────────────────────────────────────────────

window.goPage = async function(page) {
  // 유효하지 않은 페이지 번호면 API 호출 차단
  if (page < 1 || (totalPages > 0 && page > totalPages)) return;
  await load(page);
};

async function load(page) {
  try {
    const data = await fetchHistory(page, PAGE_SIZE);
    if (!data) return;
    currentPage = page;  // API한테 현재 페이지 묻는 대신, 이 함수에서 직접 기억하기
    totalPages = Math.ceil((data.total || 0) / PAGE_SIZE);  // 전체 페이지 수 계산해서 저장
    renderTable(data.items);
    renderTrendChart(data.items);
    renderPagination(data.total, currentPage, PAGE_SIZE);
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
