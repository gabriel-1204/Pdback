import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# uvicorn -> docs
# 가입 -> 로그인 -> 토큰 authorize에 넣기
# powershell에서 python feedback_test.py

# jwt.io에서 확인한 user_id (sub 값) 여기에 입력
USER_ID = "user_id"

async def insert():
    """docs에서 feedback api 3개 테스트하려고 만든 데이터 삽입용"""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['pdback']

    await db['interviews'].delete_one({'_id': 'test-session-001'})
    await db['feedbacks'].delete_one({'interview_id': 'test-session-001'})

    await db['interviews'].insert_one({
        '_id': 'test-session-001',
        'user_id': USER_ID,
        'position': '백엔드',
        'tech_stack': ['Python', 'FastAPI'],
        'career_years': 1,
        'eye_contact': 75,
        'posture_safety_rate': 85,
        'questions': [
            {
                'question_number': 1,
                'question_content': 'FastAPI란 무엇인가요?',
                'model_answer': 'FastAPI는 Python 기반 고성능 웹 프레임워크입니다.',
                'question_keywords': ['FastAPI', 'Python'],
                'category': '기술',
                'expected_duration_seconds': 120,
                'created_at': datetime.now(),
                'answer': {
                    'answer_content': '파이썬 웹 프레임워크입니다.',
                    'stt_raw_text': None,
                    'started_at': datetime.now(),
                    'ended_at': datetime.now(),
                    'duration_seconds': 30,
                    'status': 'submitted'
                }
            }
        ],
        'status': 'finished',
        'created_at': datetime.now()
    })
    print('삽입 완료! session_id: test-session-001')
    client.close()

asyncio.run(insert())
