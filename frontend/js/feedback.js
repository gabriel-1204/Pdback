const API_BASE = '/api/v1';

// ── 유틸 ─────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('access_token');
}

// 로그아웃 링크 연결
window.logout = async function() {
  const token = getToken();
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  } catch (error) {
    // 로그아웃 요청 실패해도 토큰 삭제 후 로그인페이지 이동(유선님따라 추가^^)
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

function showError(msg) {
  document.getElementById('loading-state').style.display = 'none';
  document.getElementById('error-state').style.display  = 'block';
  document.getElementById('error-message').textContent  = msg;
}

function scoreClass(score, max) {
  const ratio = score / max;
  if (ratio >= 0.7) return 'high';
  if (ratio >= 0.4) return 'mid';
  return 'low';
}

// ── API 호출 ──────────────────────────────────────────────────────────

async function generateFeedback(sessionId, token) {
  const res = await fetch(`${API_BASE}/feedback/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ session_id: sessionId })
  });

  if (res.status === 401) {
    window.location.href = 'login.html';
    return null;
  }
  if (res.status === 409) {
    // 이미 생성된 피드백 → GET으로 조회
    return await getFeedback(sessionId, token);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || '피드백 생성에 실패했습니다.');
  }
  return await res.json();
}

async function getFeedback(interviewId, token) {
  const res = await fetch(`${API_BASE}/feedback/${interviewId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (res.status === 401) {
    window.location.href = 'login.html';
    return null;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || '피드백 조회에 실패했습니다.');
  }
  return await res.json();
}

// ── 렌더링 ────────────────────────────────────────────────────────────

function renderFeedback(data) {
  // 헤더 서브타이틀 (localStorage에서 직무 정보 읽기)
  const jobRole   = localStorage.getItem('job_role') || '-';
  const techStack = (() => {
    try { return JSON.parse(localStorage.getItem('tech_stack') || '[]'); } catch { return []; }
  })();
  const expYears  = localStorage.getItem('experience_years') ?? '-';

  const interviewDate = new Date(data.created_at).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });

  document.getElementById('feedback-subtitle').textContent =
    `${interviewDate}  |  ${jobRole}  |  ${techStack.length ? techStack.join(', ') : '-'}  |  경력 ${expYears}년`;

  // 점수 카드
  const techScore     = Number(data.technical_score).toFixed(1);
  const logicScore    = Number(data.logic_score).toFixed(1);
  const attitudeScore = Number(data.posture_summary.attitude_score).toFixed(1);

  document.getElementById('tech-score').textContent     = techScore;
  document.getElementById('logic-score').textContent    = logicScore;
  document.getElementById('attitude-score').textContent = attitudeScore;

  // 바 차트 (최대 높이 160px)
  const BAR_MAX = 160;
  function setBar(id, valId, score, max, suffix) {
    const ratio = Math.min(score / max, 1);
    document.getElementById(id).style.height    = (ratio * BAR_MAX) + 'px';
    document.getElementById(valId).textContent  = Number(score || 0).toFixed(1) + suffix;
  }
  // 0~10 스케일
  setBar('bar-tech',    'bar-val-tech',    data.technical_score, 10,  '');
  setBar('bar-logic',   'bar-val-logic',   data.logic_score,     10,  '');
  setBar('bar-keyword', 'bar-val-keyword', data.keyword_score,   10,  '');
  // 0~100 스케일
  setBar('bar-eyes',    'bar-val-eyes',    data.posture_summary.eyes_score,    100, '%');
  setBar('bar-posture', 'bar-val-posture', data.posture_summary.posture_score, 100, '%');

  // 종합 코멘트
  document.getElementById('interview-comment').textContent = data.interview_comment || '-';

  // 태도 코멘트
  document.getElementById('posture-comment').textContent =
    data.posture_summary.posture_comment || '-';

  // 강점
  const strengthsList = document.getElementById('strengths-list');
  strengthsList.innerHTML = '';
  (data.strengths || []).forEach(text => {
    const li = document.createElement('li');
    li.className = 'strength';
    li.textContent = text;
    strengthsList.appendChild(li);
  });
  if (!data.strengths || !data.strengths.length) {
    strengthsList.innerHTML = '<li class="strength" style="color:#aaa;">강점 정보가 없습니다.</li>';
  }

  // 개선점
  const improveList = document.getElementById('improvements-list');
  improveList.innerHTML = '';
  (data.improvements || []).forEach(text => {
    const li = document.createElement('li');
    li.className = 'improve';
    li.textContent = text;
    improveList.appendChild(li);
  });
  if (!data.improvements || !data.improvements.length) {
    improveList.innerHTML = '<li class="improve" style="color:#aaa;">개선점 정보가 없습니다.</li>';
  }

  // 질문별 피드백
  const qContainer = document.getElementById('question-feedbacks');
  qContainer.innerHTML = '';
  (data.question_feedbacks || []).forEach(qf => {
    const cls    = scoreClass(qf.score, 10);
    const item   = document.createElement('div');
    item.className = 'question-item';
    item.innerHTML = `
      <div class="question-header">
        <span class="q-title">Q${qf.question_number}. ${escapeHtml(qf.question_content)}</span>
        <span class="q-score ${cls}">${Number(qf.score).toFixed(1)} / 10</span>
        <span class="q-toggle">▼</span>
      </div>
      <div class="question-body">
        <div class="q-section">
          <div class="q-section-label">내 답변</div>
          <div class="q-section-text answer">${escapeHtml(qf.answer_content || '(답변 없음)')}</div>
        </div>
        <div class="q-section">
          <div class="q-section-label">모범 답안</div>
          <div class="q-section-text model">${escapeHtml(qf.model_answer || '-')}</div>
        </div>
        <div class="q-section">
          <div class="q-section-label">AI 평가</div>
          <div class="q-section-text comment">${escapeHtml(qf.comment)}</div>
        </div>
      </div>
    `;
    qContainer.appendChild(item);
  });

  // 질문 아코디언 이벤트 위임 등록
  qContainer.addEventListener('click', function(e) {
    const header = e.target.closest('.question-header');
    if (header) toggleQuestion(header);
  });

  // 콘텐츠 표시
  document.getElementById('loading-state').style.display  = 'none';
  document.getElementById('feedback-content').style.display = 'block';
}

// ── 아코디언 토글 ─────────────────────────────────────────────────────

function toggleQuestion(header) {
  const body = header.nextElementSibling;
  const isOpen = header.classList.toggle('open');
  body.classList.toggle('open', isOpen);
}

// ── XSS 방지 ─────────────────────────────────────────────────────────

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── 진입점 ────────────────────────────────────────────────────────────

async function init() {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  const params    = new URLSearchParams(window.location.search);
  const sessionId = params.get('session_id');
  const feedbackId = params.get('id');

  try {
    let data;
    if (sessionId) {
      data = await generateFeedback(sessionId, token);
    } else if (feedbackId) {
      data = await getFeedback(feedbackId, token);
    } else {
      showError('피드백 ID가 없습니다. 올바른 경로로 접근해주세요.');
      return;
    }
    if (data) renderFeedback(data);
  } catch (e) {
    showError(e.message);
  }
}

init();
