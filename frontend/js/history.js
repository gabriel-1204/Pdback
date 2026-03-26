// 로그인 체크
if (!localStorage.getItem('access_token')) {
    alert('로그인이 필요합니다.');
    window.location.href = '/login';
}

const API_BASE = '/api/v1';


// 로그아웃 링크 연결
window.logout = async function() {
    const token = localStorage.getItem('access_token');
    try {
        await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
        });
    } catch (error) {
        // 로그아웃 요청 실패해도 토큰 삭제 후 로그인페이지 이동
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
}
