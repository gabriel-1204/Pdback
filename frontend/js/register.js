      document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password-confirm').value;
        const position = document.getElementById('position').value || null; //포지션은 선택값이라 입력없으면 null로 출력

        //폼 유효성 검사
        if (!username) { alert('이름을 입력해주세요.'); return; }
        if (!email) { alert('이메일을 입력해주세요.'); return; }
        if (!password) { alert('비밀번호를 입력해주세요.'); return; }
        if (password.length < 8) { alert('비밀번호는 8자 이상 입력해주세요.'); return; }
        if (password !== passwordConfirm) {alert('비밀번호가 일치하지 않습니다.'); return; }

        //백엔드 API 연동
        try {
          const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, position }),
          });

          const data = await response.json();

          //회원가입 성공시
          if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            window.location.href = '/start'; //면접페이지로 이동
          } else {
            alert(data.detail);
          }
        } catch (e) {
          alert('네트워크 오류가 발생했습니다.');
        }
      });
