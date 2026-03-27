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

        await db['interviews'].insert_one({
            '_id': sid,
            'user_id': USER_ID,
            'position': s["position"],
            'tech_stack': s["tech_stack"],
            'career_years': s["career_years"],
            'eye_contact': s["eye_contact"],
            'posture_safety_rate': s["posture_safety_rate"],
            'questions': [
                {
                    'question_number': 1,
                    'question_content': f'{s["position"]} 관련 기술 질문입니다.',
                    'model_answer': '모범 답안입니다.',
                    'question_keywords': s["tech_stack"],
                    'category': '기술',
                    'expected_duration_seconds': 120,
                    'created_at': created_at,
                    'answer': {
                        'answer_content': '테스트 답변입니다.',
                        'stt_raw_text': None,
                        'started_at': created_at,
                        'ended_at': created_at,
                        'duration_seconds': 60,
                        'status': 'submitted'
                    }
                }
            ],
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
                    {
                        'question_number': 1,
                        'score': s["technical_score"],
                        'comment': '기술적 이해도가 좋습니다.',
                    }
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
