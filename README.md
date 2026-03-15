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
app/
├── main.py          # FastAPI 앱 진입점
├── config.py        # 환경변수 설정
├── database.py      # MongoDB 연결 관리
├── api/v1/          # API 라우터
├── domain/
│   ├── interview/   # 면접 세션 도메인
│   └── feedback/    # 피드백 도메인
└── services/
    └── gemini.py    # Gemini API 클라이언트
```
