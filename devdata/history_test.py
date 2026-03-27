import asyncio
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient

# 사용법:
# 1. uvicorn 실행 후 docs에서 회원가입 → 로그인 → jwt.io에서 sub(user_id) 확인
# 2. USER_ID에 입력
# 3. powershell에서: python history_test.py

# jwt.io에서 확인한 user_id (sub 값) 여기에 입력
USER_ID = "user_id"

KST = timezone(timedelta(hours=9))

# 테스트용 면접/피드백 데이터 5개
SESSIONS = [
    {
        "session_id": "hist-test-001",
        "position": "백엔드",
        "tech_stack": ["Python", "FastAPI"],
        "career_years": 1,
        "eye_contact": 75,
        "posture_safety_rate": 85,
        "days_ago": 10,
        "interview_score": 6.0,
        "technical_score": 6.5,
        "logic_score": 5.5,
        "keyword_score": 6.0,
        "attitude_score": 6.9,
        "eyes_score": 75.0,
        "posture_score": 85.0,
    },
    {
        "session_id": "hist-test-002",
        "position": "백엔드",
        "tech_stack": ["Python", "Django"],
        "career_years": 1,
        "eye_contact": 60,
        "posture_safety_rate": 70,
        "days_ago": 8,
        "interview_score": 5.0,
        "technical_score": 5.0,
        "logic_score": 4.5,
        "keyword_score": 5.5,
        "attitude_score": 5.8,
        "eyes_score": 60.0,
        "posture_score": 70.0,
    },
    {
        "session_id": "hist-test-003",
        "position": "풀스택",
        "tech_stack": ["React", "Node.js"],
        "career_years": 2,
        "eye_contact": 80,
        "posture_safety_rate": 75,
        "days_ago": 5,
        "interview_score": 6.7,
        "technical_score": 7.0,
        "logic_score": 6.5,
        "keyword_score": 6.5,
        "attitude_score": 7.1,
        "eyes_score": 80.0,
        "posture_score": 75.0,
    },
    {
        "session_id": "hist-test-004",
        "position": "백엔드",
        "tech_stack": ["Java", "Spring"],
        "career_years": 1,
        "eye_contact": 85,
        "posture_safety_rate": 90,
        "days_ago": 3,
        "interview_score": 7.5,
        "technical_score": 8.0,
        "logic_score": 7.0,
        "keyword_score": 7.5,
        "attitude_score": 8.3,
        "eyes_score": 85.0,
        "posture_score": 90.0,
    },
    {
        "session_id": "hist-test-005",
        "position": "백엔드",
        "tech_stack": ["Python", "FastAPI", "MongoDB"],
        "career_years": 1,
        "eye_contact": 90,
        "posture_safety_rate": 88,
        "days_ago": 1,
        "interview_score": 8.3,
        "technical_score": 8.5,
        "logic_score": 8.0,
        "keyword_score": 8.5,
        "attitude_score": 8.9,
        "eyes_score": 90.0,
        "posture_score": 88.0,
    },
]


async def insert():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['pdback']

    for s in SESSIONS:
        sid = s["session_id"]
        created_at = datetime.now(KST) - timedelta(days=s["days_ago"])

        # 기존 데이터 삭제 후 재삽입
        await db['interviews'].delete_one({'_id': sid})
        await db['feedbacks'].delete_one({'interview_id': sid})

        questions = [
            {
                'question_number': 1,
                'question_content': f'{s["position"]} 직무에서 주로 사용하는 기술 스택을 설명해주세요.',
                'model_answer': f'{", ".join(s["tech_stack"])}의 특징과 장점을 설명하는 모범 답안입니다.',
                'question_keywords': s["tech_stack"],
                'category': '기술',
                'expected_duration_seconds': 120,
                'created_at': created_at,
                'answer': {'answer_content': '테스트 답변입니다.', 'stt_raw_text': None, 'started_at': created_at, 'ended_at': created_at, 'duration_seconds': 60, 'status': 'submitted'}
            },
            {
                'question_number': 2,
                'question_content': f'{s["tech_stack"][0]}에서 RESTful API를 설계할 때 고려해야 할 사항을 설명해주세요.',
                'model_answer': 'RESTful API 설계 원칙(무상태성, 자원 중심 URI, HTTP 메서드 활용 등)을 설명하는 모범 답안입니다.',
                'question_keywords': ['REST', 'API', 'HTTP'],
                'category': '기술',
                'expected_duration_seconds': 120,
                'created_at': created_at,
                'answer': {'answer_content': '테스트 답변입니다.', 'stt_raw_text': None, 'started_at': created_at, 'ended_at': created_at, 'duration_seconds': 65, 'status': 'submitted'}
            },
            {
                'question_number': 3,
                'question_content': '데이터베이스 인덱스의 동작 원리와 사용 시 주의사항을 설명해주세요.',
                'model_answer': '인덱스 구조(B-Tree 등), 조회 성능 향상 원리, 과도한 인덱스로 인한 쓰기 성능 저하 등을 설명하는 모범 답안입니다.',
                'question_keywords': ['데이터베이스', '인덱스', '성능'],
                'category': '기술',
                'expected_duration_seconds': 120,
                'created_at': created_at,
                'answer': {'answer_content': '테스트 답변입니다.', 'stt_raw_text': None, 'started_at': created_at, 'ended_at': created_at, 'duration_seconds': 70, 'status': 'submitted'}
            },
            {
                'question_number': 4,
                'question_content': f'{s["position"]} 개발 시 성능 최적화 경험을 말씀해주세요.',
                'model_answer': '성능 병목 원인 분석 및 최적화 방법을 설명하는 모범 답안입니다.',
                'question_keywords': ['성능', '최적화', '트러블슈팅'],
                'category': '기술',
                'expected_duration_seconds': 150,
                'created_at': created_at,
                'answer': {'answer_content': '테스트 답변입니다.', 'stt_raw_text': None, 'started_at': created_at, 'ended_at': created_at, 'duration_seconds': 80, 'status': 'submitted'}
            },
            {
                'question_number': 5,
                'question_content': f'{s["tech_stack"][0]} 환경에서 발생한 버그를 디버깅한 경험을 설명해주세요.',
                'model_answer': '문제 재현 → 원인 분석 → 수정 → 검증 순서로 디버깅 과정을 설명하는 모범 답안입니다.',
                'question_keywords': ['디버깅', '트러블슈팅', s["tech_stack"][0]],
                'category': '기술',
                'expected_duration_seconds': 120,
                'created_at': created_at,
                'answer': {'answer_content': '테스트 답변입니다.', 'stt_raw_text': None, 'started_at': created_at, 'ended_at': created_at, 'duration_seconds': 65, 'status': 'submitted'}
            },
        ]

        await db['interviews'].insert_one({
            '_id': sid,
            'user_id': USER_ID,
            'position': s["position"],
            'tech_stack': s["tech_stack"],
            'career_years': s["career_years"],
            'eye_contact': s["eye_contact"],
            'posture_safety_rate': s["posture_safety_rate"],
            'questions': questions,
            'status': 'finished',
            'created_at': created_at,
        })

        await db['feedbacks'].insert_one({
            'interview_id': sid,
            'user_id': USER_ID,
            'ai_feedback': {
                'interview_score': s["interview_score"],
                'technical_score': s["technical_score"],
                'logic_score': s["logic_score"],
                'keyword_score': s["keyword_score"],
                'interview_comment': f'{s["position"]} 면접 테스트 종합 코멘트입니다.',
                'strengths': ['답변이 명확했습니다.', '핵심 키워드를 잘 활용했습니다.'],
                'improvements': ['더 구체적인 사례를 들면 좋겠습니다.'],
                'question_feedbacks': [
                    {'question_number': 1, 'score': s["technical_score"], 'comment': '기술 스택에 대한 이해도가 좋습니다.'},
                    {'question_number': 2, 'score': s["logic_score"],     'comment': 'API 설계 원칙을 잘 이해하고 있습니다.'},
                    {'question_number': 3, 'score': s["logic_score"],     'comment': '데이터베이스 인덱스 개념을 정확히 설명했습니다.'},
                    {'question_number': 4, 'score': s["technical_score"], 'comment': '성능 최적화 경험을 구체적으로 서술했습니다.'},
                    {'question_number': 5, 'score': s["keyword_score"],   'comment': '디버깅 접근 방식이 체계적입니다.'},
                ],
            },
            'posture_summary': {
                'eyes_score': s["eyes_score"],
                'posture_score': s["posture_score"],
                'attitude_score': s["attitude_score"],
                'posture_comment': '시선 처리와 자세가 전반적으로 안정적이었습니다.',
            },
            'created_at': created_at,
        })

        print(f'삽입 완료: {sid} ({s["position"]}, {created_at.strftime("%Y-%m-%d")})')

    print(f'\n총 {len(SESSIONS)}개 삽입 완료. 히스토리 페이지: http://localhost:8000/history')
    client.close()


asyncio.run(insert())
