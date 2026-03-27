// 토큰 자동 갱신이 포함된 공통 fetch wrapper
// 401 응답 시 refresh_token으로 재발급 후 원래 요청을 자동 재시도
async function authFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/login';
    return null;
  }

  // Authorization 헤더 자동 추가
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };

  const response = await fetch(url, options);

  // 401이 아니면 그대로 반환
  if (response.status !== 401) return response;

  // refresh_token으로 새 토큰 발급 시도
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    window.location.href = '/login';
    return null;
  }

  const refreshRes = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  if (!refreshRes.ok) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    return null;
  }

  const data = await refreshRes.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);

  // 새 토큰으로 원래 요청 재시도
  options.headers['Authorization'] = `Bearer ${data.access_token}`;
  return fetch(url, options);
}
