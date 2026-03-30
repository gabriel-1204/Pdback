// 공통 유틸리티 함수

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
