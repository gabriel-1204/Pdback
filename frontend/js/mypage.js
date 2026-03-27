(function() {
      //저장된 access_token 가져오기(만료 시 갱신 후 재할당)
      let token = localStorage.getItem('access_token');
      let originalPosition = '';

      //토큰이 없음=로그인 하지않음 , 로그인페이지로 이동
      if (!token) { alert('로그인이 필요합니다.'); window.location.href = '/login'; return; }

      //사용자 정보 로드(내 정보 가져와서 보여주기 작업)
      //토큰이 있으면 로그인한 사람 - 없으면 로그인 안한사람
      //상대경로사용하여 배포시 자동으로 경로 맞춰지도록 설정
      async function loadUserInfo() {
        try {
          const response = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
          });

          // access_token 만료 시(401) refresh_token으로 새 토큰 발급 후 재시도
          if (response.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) { window.location.href = '/login'; return; }

            const refreshResponse = await fetch('/api/v1/auth/refresh', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh_token: refreshToken })
            });

            //리프레시토큰도 만료되면 로그인페이지로 이동
            if (!refreshResponse.ok) { window.location.href = '/login'; return; }

            const refreshData = await refreshResponse.json();
            token = refreshData.access_token; //새토큰 받으면
            localStorage.setItem('access_token', token); //업데이트
            localStorage.setItem('refresh_token', refreshData.refresh_token);
            return loadUserInfo();
          }

          //토큰만료 외 에러 시 로그인페이지로 이동
          if (!response.ok) {
            window.location.href = '/login';
            return;
          }


          const user = await response.json();
          document.getElementById('profile-name').textContent = user.username; //프로필칸 유저정보 표시용
          document.getElementById('profile-email').textContent = user.email;
          document.getElementById('profile-position').textContent = '희망 직무 : ' + (user.position || '--'); //직무
          document.getElementById('input-username').value = user.username; //이름 수정 폼 입력칸
          document.getElementById('input-email').value = user.email; //이메일 수정불가능 , 그냥 현재 이메일(아이디) 보여주기
          originalPosition = user.position || ''; //희망 직무 선택
          document.getElementById('input-position').value = originalPosition;
          console.log('originalPosition:', originalPosition);
        } catch (error) {
          alert('사용자 정보를 불러오는 데 실패했습니다.');
        }
      }

      //취소 버튼 - 입력 중인 내용을 원래 정보로 되돌리기
      document.getElementById('btn-cancel').addEventListener('click', () => {
        loadUserInfo();
      });

      //프로필 수정(이름,비밀번호)
      document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('input-username').value.trim();
        const position = document.getElementById('input-position').value || undefined;
        const currentPassword = document.getElementById('input-current-password').value;
        const newPassword = document.getElementById('input-new-password').value;
        const confirmPassword = document.getElementById('input-confirm-password').value;

        //수정사항 없을 때 체크
        const originalUsername = document.getElementById('profile-name').textContent.trim();
        const currentPosition = document.getElementById('input-position').value || '';
        const hasChanges = username !== originalUsername || currentPosition !== originalPosition || currentPassword || newPassword;
        if (!hasChanges) {
          alert('수정된 사항이 없습니다.');
          return;
        }

        const clearPasswords = () => {
          document.getElementById('input-current-password').value = '';
          document.getElementById('input-new-password').value = '';
          document.getElementById('input-confirm-password').value = '';
        };

        //새로운 비밀번호 입력했을 때만 유효성 검사
        //이름만 변경, 비밀번호만 변경, 둘다 변경 가능
        if (newPassword) {
          if (!currentPassword) {
            alert('현재 비밀번호를 입력해주세요.');
            clearPasswords();
            return;
          }
          if (newPassword.length < 8) {
            alert('비밀번호는 8자 이상이어야 합니다.');
            clearPasswords();
            return;
          }
          if (newPassword !== confirmPassword) {
            alert('새 비밀번호가 일치하지 않습니다.');
            clearPasswords();
            return;
          }
        }

        try {
          const response = await fetch('/api/v1/auth/me', {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              username,
              position,
              current_password: currentPassword || undefined, //변경된 값있으면 전송, 없으면 제외
              new_password: newPassword || undefined,
            })
          });

          if (response.ok) {
            alert('프로필이 수정되었습니다.'); //수정후에
            loadUserInfo(); //다시 실행
            clearPasswords();
          } else {
            const errorData = await response.json();
            const message = Array.isArray(errorData.detail)
              ? errorData.detail.map(e => e.msg).join('\n')
              : errorData.detail;
            alert(message);
            clearPasswords();
          }
        } catch (error) {
          alert('네트워크 오류가 발생했습니다. 다시 시도해주세요.');
        }
      });

      //회원 탈퇴 - 모달 열기
      document.getElementById('btn-withdraw').addEventListener('click', () => {
        if (!confirm('정말 탈퇴하시겠습니까?')) return;
        const modal = document.getElementById('modal-withdraw');
        modal.style.display = 'flex';
        document.getElementById('modal-password').value = '';
      });

      //모달 취소
      document.getElementById('modal-cancel').addEventListener('click', () => {
        document.getElementById('modal-withdraw').style.display = 'none';
      });

      //모달 탈퇴 확인
      document.getElementById('modal-confirm').addEventListener('click', async () => {
        const password = document.getElementById('modal-password').value;
        if (!password) { alert('비밀번호를 입력해주세요.'); return; }

        try {
          const response = await fetch('/api/v1/auth/me', {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
          });

          if (!response.ok) {
            alert('회원 탈퇴에 실패했습니다.');
            return;
          }
        } catch (error) {
          alert('네트워크 오류가 발생했습니다.');
          return;
        }

        localStorage.removeItem('access_token'); //토큰 삭제하고
        localStorage.removeItem('refresh_token');
        window.location.href = '/login'; //로그인페이지 이동
      });

      // 통계 데이터 로드
      async function loadStats() {
        try {
          const res = await fetch('/api/v1/feedback/stats', { headers: { 'Authorization': `Bearer ${token}` } });

          if (res.ok) {
            const data = await res.json();
            document.getElementById('stat-weekly').textContent = data.weekly_count;
            document.getElementById('stat-total').textContent = data.total_count;
            document.getElementById('stat-avg').textContent = data.avg_score;
            document.getElementById('stat-best').textContent = data.best_score;
          }
        } catch (error) {
          console.error('통계 데이터를 불러오는 데 실패했습니다.', error);
        }
      }

      //토큰 있으면 사용자 정보 화면에 표시
      loadUserInfo();
      loadStats();
    })();
