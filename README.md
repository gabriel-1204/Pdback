# P:dback Backend

Vision AI와 STT가 결합된 개발자 맞춤형 실전 화상 면접 솔루션 - FastAPI 백엔드

## 기술 스택

- **Framework**: FastAPI (Python 3.11)
- **Database**: MongoDB + Motor (async driver)
- **AI**: Google Gemini API
- **Infra**: Docker, AWS EC2, GitHub Actions

## 로컬 실행

### 1. 환경 설정

```bash
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 등 설정
```

### 2-A. pip으로 실행

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2-B. Docker로 실행

```bash
docker compose up --build
```

## API 문서

서버 실행 후 아래 주소에서 Swagger UI 확인:

- http://localhost:8000/docs

## 린터 (Ruff)

코드 품질 유지를 위해 [Ruff](https://docs.astral.sh/ruff/)를 사용합니다. 설정은 `pyproject.toml`에 정의되어 있습니다.

```bash
# 설치
pip install ruff

# 린트 검사
ruff check app/

# 자동 수정
ruff check app/ --fix

# 코드 포맷팅
ruff format app/
```

## 프로젝트 구조

```
app/                             # 백엔드 (FastAPI)
├── main.py                      # FastAPI 앱 진입점
├── config.py                    # 환경변수 설정
├── database.py                  # MongoDB 연결 관리
├── api/v1/
│   └── router.py                # API 라우터 통합
├── domain/
│   ├── user/                    # 김유선
│   │   └── models.py                # 유저 문서 스키마
│   ├── interview/               # 이영진
│   │   ├── models.py                # 면접 문서 스키마
│   │   ├── schema.py                # 요청/응답 DTO
│   │   ├── router.py                # 면접 API 엔드포인트
│   │   ├── service.py               # 비즈니스 로직
│   │   └── prompt.py                # Gemini 프롬프트 템플릿 (김평일)
│   └── feedback/                # 박지영
│       ├── models.py                # 피드백 문서 스키마
│       ├── schema.py                # 요청/응답 DTO
│       ├── router.py                # 피드백 API 엔드포인트
│       └── service.py               # 비즈니스 로직
└── services/
    └── gemini.py                    # Gemini API 클라이언트 (김평일)
frontend/                        # 프론트엔드 (HTML/CSS/JS)
├── index.html                   # 랜딩 페이지
├── css/
│   └── common.css               # 공통 스타일
└── pages/
    ├── login.html               # 로그인 (김유선)
    ├── register.html            # 회원가입 (김유선)
    ├── mypage.html              # 마이페이지 (김유선)
    ├── interview-setup.html     # 면접 설정 (김평일)
    ├── interview.html           # 면접 진행 (이영진)
    ├── feedback.html            # 피드백 결과 (박지영)
    └── history.html             # 면접 히스토리 (박지영)
```

---

## Git 작업 가이드

### 0. Git 명령어 기본 용어

| 용어 | 의미 | 예시 |
|------|------|------|
| `origin` | GitHub 원격 저장소의 별명 | `origin` = `https://github.com/gabriel-1204/Pdback.git` |
| `feature/infra` | 내 컴퓨터(로컬)의 브랜치 | `git checkout feature/infra` → 로컬 브랜치 이동 |
| `origin/main` | GitHub(원격)의 main 브랜치 | `git merge origin/main` → GitHub의 main 코드를 가져와 합치기 |

**origin을 붙이는 기준:**
- **내 컴퓨터에서 이동**할 때 → origin 안 붙임 (`git checkout feature/infra`)
- **GitHub의 코드를 참조**할 때 → origin 붙임 (`git merge origin/main`, `git push origin 내브랜치`)

자주 쓰는 명령어 정리:

| 명령어 | 하는 일 |
|--------|---------|
| `git fetch origin` | GitHub에서 최신 정보를 가져옴 (내 코드는 안 바뀜) |
| `git merge origin/main` | GitHub의 main 코드를 내 브랜치에 합침 |
| `git checkout 브랜치명` | 다른 브랜치로 이동 |
| `git status` | 변경된 파일 목록 확인 |
| `git add 파일명` | 커밋할 파일을 지정 |
| `git commit -m "메시지"` | 변경사항을 저장 (커밋) |
| `git push origin 브랜치명` | 내 커밋을 GitHub에 업로드 |

### 1. PR 올리기 전 main 최신화 필수

PR을 올리기 전에 반드시 최신 main을 내 브랜치에 반영해야 합니다.
하루 중간에 다른 팀원이 PR을 머지했을 수 있으므로, **작업 시작 전과 PR 전에** 최신화해주세요.

```bash
git fetch origin
git merge origin/main
# 충돌이 있으면 해결 후 커밋
```

> 추가로 매일 일과 종료 후 팀장이 모든 feature 브랜치를 일괄 최신화합니다.

### 2. `git add .` 사용 금지 — 본인 파일만 지정해서 add

`git add .`이나 `git add -A`를 사용하면 **본인이 수정하지 않은 파일까지 커밋에 포함**됩니다.
이렇게 되면 다른 팀원의 작업을 자기 브랜치 버전으로 덮어쓰는 사고가 발생합니다.

#### 올바른 커밋 순서

```bash
# 1단계: 변경된 파일 목록 확인
git status

# 2단계: 본인이 작업한 파일만 골라서 추가
git add app/domain/feedback/service.py
git add app/domain/feedback/models.py

# 3단계: 스테이징된 파일이 내 것만인지 다시 확인
git diff --staged --stat

# 4단계: 커밋
git commit -m "[feedback] 피드백 서비스 함수 구현"
```

#### 여러 파일을 한번에 추가하고 싶을 때

```bash
# 특정 폴더 안의 파일만 추가 (본인 담당 폴더)
git add app/domain/feedback/

# 또는 파일을 나열해서 추가
git add app/domain/feedback/service.py app/domain/feedback/models.py
```

#### 실수로 다른 파일까지 add 했을 때

```bash
# 특정 파일을 스테이징에서 제거 (파일 내용은 유지됨)
git restore --staged app/config.py
```

#### 이미 커밋까지 해버렸을 때 (아직 push 안 한 경우)

```bash
# 직전 커밋을 취소 (변경사항은 그대로 유지됨)
git reset HEAD~1

# 내 파일만 다시 add
git add app/domain/feedback/service.py
git add app/domain/feedback/models.py

# 다시 커밋
git commit -m "[feedback] 피드백 서비스 함수 구현"
```

### 3. 공통 파일 수정 시 팀 공유

아래 파일들은 여러 파트에서 사용하므로, 수정 전에 반드시 팀에 알려주세요.
사전 공유 없이 수정하면 머지 시 충돌이나 덮어쓰기가 발생할 수 있습니다.

| 공통 파일 | 역할 |
|-----------|------|
| `app/config.py` | 환경변수 설정 |
| `app/database.py` | MongoDB 연결 관리 |
| `app/main.py` | FastAPI 앱 진입점 |
| `requirements.txt` | 패키지 의존성 |

공통 파일 수정이 필요하면:
1. 팀 채팅에 수정 내용 공유
2. **별도 PR로 먼저 머지**
3. 나머지 팀원이 `git fetch origin && git merge origin/main`으로 반영
4. 추가로 팀장이 일과 종료 시 각 브랜치를 일괄 최신화합니다

### 4. 전체 작업 흐름 요약

```
작업 시작
  └─ git fetch origin && git merge origin/main   (최신화)
  └─ 코드 작업
  └─ git status                                   (변경 파일 확인)
  └─ git add 내파일만                              (본인 파일만 추가)
  └─ git diff --staged --stat                     (스테이징 확인)
  └─ git commit -m "[파트] 작업내용"                (커밋)
  └─ git fetch origin && git merge origin/main    (PR 전 다시 최신화)
  └─ git push origin 내브랜치                      (푸시)
  └─ GitHub에서 PR 생성
```

> 추가로 매일 일과 종료 후 팀장이 모든 feature 브랜치를 일괄 최신화합니다.
