// 로그인/로그아웃 버튼 상태 관리
(function () {
    const authBtn = document.getElementById('auth-btn');
    if (!authBtn) return;

    const token = localStorage.getItem('access_token');

    if (token) {
        authBtn.textContent = '로그아웃';
        authBtn.href = '#';
        authBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/api/v1/auth/logout', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
                });
            } catch (_) {}
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        });
    } else {
        authBtn.textContent = '로그인';
        authBtn.href = '/login';
    }
})();
