// 로그인 체크
if (!localStorage.getItem('access_token')) {
    alert('로그인이 필요합니다.');
    window.location.href = '/login';
}

// 뒤로가기 체크(로그아웃 후 뒤로가기 했을 때 alert+리다이렉트)
window.addEventListener('pageshow', () => {
  if (!localStorage.getItem('access_token')) {
    alert('로그인이 필요합니다.');
    window.location.href = '/login';
  }
});

// ========================================
// 1. 직무별 기술 스택 목록
// ========================================
const STACK_BY_ROLE = {
  '백엔드':     ['Python', 'Java', 'Node.js', 'FastAPI', 'Spring', 'Django',
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'AWS'],
  '프론트엔드': ['JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
                'Next.js', 'HTML', 'CSS', 'Tailwind', 'Webpack'],
  '풀스택':     ['JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
                'Python', 'FastAPI', 'MySQL', 'MongoDB', 'Docker'],
  '데이터':     ['Python', 'R', 'SQL', 'Pandas', 'NumPy', 'TensorFlow',
                'PyTorch', 'Spark', 'Hadoop', 'Tableau', 'AWS'],
  'DevOps':    ['Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'Jenkins',
                'GitHub Actions', 'Terraform', 'Linux', 'Nginx', 'Kafka'],
};

const techStacks = [];
const stackTagsContainer = document.querySelector('.stack-tags');

// ========================================
// 2. 기술 스택 선택 버튼 렌더링 함수
// ========================================
const renderStackButtons = (role) => {
  techStacks.length = 0;
  stackTagsContainer.innerHTML = '';

  const stacks = STACK_BY_ROLE[role] || [];

  stacks.forEach(stackName => {
    const btn = document.createElement('div');
    btn.className = 'radio-mock';
    btn.textContent = stackName;

    btn.addEventListener('click', () => {
      if (techStacks.includes(stackName)) {
        const index = techStacks.indexOf(stackName);
        techStacks.splice(index, 1);
        btn.classList.remove('selected');
      } else {
        if (techStacks.length >= 3) {
          alert('기술 스택은 최대 3개까지 선택 가능합니다.');
          return;
        }
        techStacks.push(stackName);
        btn.classList.add('selected');
      }
    });

    stackTagsContainer.appendChild(btn);
  });
};

// ========================================
// 3. 직무 선택 클릭 이벤트
// ========================================
const jobRoleGroup = document.querySelector('#job-role-group');

jobRoleGroup.querySelectorAll('.radio-mock').forEach(item => {
  item.addEventListener('click', () => {
    jobRoleGroup.querySelectorAll('.radio-mock').forEach(i => i.classList.remove('selected'));
    item.classList.add('selected');
    renderStackButtons(item.textContent.trim());
  });
});

// ========================================
// 4. 경력 연차 선택 클릭 이벤트
// ========================================
const experienceGroup = document.querySelector('#experience-group');

experienceGroup.querySelectorAll('.radio-mock').forEach(item => {
  item.addEventListener('click', () => {
    experienceGroup.querySelectorAll('.radio-mock').forEach(i => i.classList.remove('selected'));
    item.classList.add('selected');
  });
});

// ========================================
// 5. 페이지 로드 시 기본값 렌더링 (백엔드)
// ========================================
renderStackButtons('백엔드');

// ========================================
// 6. 카메라/마이크 권한 요청
// ========================================
const permItems = document.querySelectorAll('.perm-item');
const micStatus = permItems[1].querySelector('.perm-status');
const cameraStatus = permItems[0].querySelector('.perm-status');

let isMicAllowed = false;
let isCameraAllowed = false;

navigator.mediaDevices.getUserMedia({ video: true })
  .then((stream) => {
    isCameraAllowed = true;
    cameraStatus.textContent = '✓ 허용됨';
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(() => {
    cameraStatus.textContent = '✗ 거부됨';
  });

navigator.mediaDevices.getUserMedia({ audio: true })
  .then((stream) => {
    isMicAllowed = true;
    micStatus.textContent = '✓ 허용됨';
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(() => {
    micStatus.textContent = '✗ 거부됨';
  });

// ========================================
// 7. 면접 시작하기 버튼 클릭 이벤트
// ========================================
const startBtn = document.querySelector('.btn-primary');

startBtn.addEventListener('click', () => {
  const jobRole = jobRoleGroup.querySelector('.radio-mock.selected')?.textContent.trim();
  const experienceText = experienceGroup.querySelector('.radio-mock.selected')?.textContent.trim();
  const experienceMap = { '신입': 0, '1~3년': 1, '3~5년': 3, '5년 이상': 5 };
  const experienceYears = experienceMap[experienceText] ?? 0;

  if (!jobRole) {
    alert('직무를 선택해주세요.');
    return;
  }
  if (techStacks.length === 0) {
    alert('기술 스택을 1개 이상 선택해주세요.');
    return;
  }
  if (micStatus.textContent === '확인 중...') {
    alert('마이크 권한 확인 중입니다. 잠시 후 다시 시도해주세요.');
    return;
  }
  if (!isMicAllowed) {
    alert('마이크 권한은 필수입니다. 허용 후 페이지를 새로고침 해주세요.');
    return;
  }
  if (!isCameraAllowed) {
    const proceed = confirm('카메라가 허용되지 않았습니다.\n카메라 없이 진행하면 태도 점수가 0점 처리될 수 있습니다.\n그래도 진행하시겠습니까?');
    if (!proceed) return;
  }
  try {
    localStorage.setItem("job_role", jobRole);
    localStorage.setItem("tech_stack", JSON.stringify(techStacks));
    localStorage.setItem("experience_years", experienceYears);
  } catch (error) {
    alert('저장 중 오류가 발생했습니다. 다시 시도해주세요.');
    return;
  }

  startBtn.disabled = true;
  startBtn.textContent = '면접 준비 중...';
  window.location.href = '/interview';
});
