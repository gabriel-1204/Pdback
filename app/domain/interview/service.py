import uuid
from datetime import datetime

from app.database import get_database
from app.domain.interview.models import Answer, InterviewDocument, Question
from app.domain.interview.prompt import build_system_prompt, get_first_question_prompt


from app.domain.interview.schema import (
    AnswerRequest,
    AnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.services.gemini import get_client, create_chat_session

MAX_QUESTIONS = 5
# 면접 세션을 생성하고 첫 질문을 반환한다.
async def start_interview(request: InterviewStartRequest) -> InterviewStartResponse:
    """면접 세션을 생성하고 첫 질문을 반환합니다."""
    # TODO: Gemini API 호출하여 첫 질문 생성

    # 1. 시스템 프롬프트 생성
    system_prompt = build_system_prompt(
        job_role=request.job_role,
        tech_stack=request.tech_stack,
        experience_years=request.experience_years,
    )

    # 2. Gemini API 호출 → 첫 질문 생성
    model = create_chat_session()

    chat = model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])
    response = chat.send_message_async(get_first_question_prompt())
    first_question = response.text.strip()

    # 3. MongoDB에 세션 저장
    session_id = str(uuid.uuid4())
    now = datetime.now()

    document = InterviewDocument(
        user_id="anonymous",          # 추후 인증 붙이면 교체
        position=request.job_role,
        tech_stack=request.tech_stack,
        career_years=request.experience_years,
        questions=[
            Question(
                question_number=1,
                question_content=first_question,
                category="기술",
                expected_duration_seconds=120,
                created_at=now,
                model_answer="",      # 추후 Gemini로 모범답안 생성 가능
                question_keywords=[],
            )
        ],
        status="in_progress",
        created_at=now,
    )
    # TODO: 세션 정보를 MongoDB에 저장
    db = get_database()
    await db["interviews"].insert_one(
        {**document.model_dump(), "_id": session_id}
    )

    # 4. 응답 반환
    return InterviewStartResponse(
        session_id=session_id,
        question=first_question,
    )

    #raise NotImplementedError

#답변을 분석하고 꼬리 질문을 생성한다.
async def submit_answer(request: AnswerRequest) -> AnswerResponse:
    """답변을 분석하고 꼬리 질문을 생성합니다."""
    db = get_database()
    now = datetime.now()

    # 1. MongoDB에서 세션 조회
    doc = await db["interviews"].find_one({"_id": request.session_id})
    if doc is None:
        raise ValueError(f"세션을 찾을 수 없습니다: {request.session_id}")

    questions: list[dict] = doc.get("questions", [])
    current_question_number = len(questions)  # 현재까지 질문 수

    # 2. 현재 질문에 답변 저장
    answer = Answer(
        answer_content=request.answer_content,
        stt_raw_text=request.stt_raw_text,
        started_at=now,   # 백엔드에서 현재 시간으로 처리
        ended_at=now,
        duration_seconds=0, # ended_at - started_at
        status="submitted",
    )

    await db["interviews"].update_one(
        {"_id": request.session_id},
        {
            "$set": {
                f"questions.{current_question_number - 1}.answer": answer.model_dump()
            }
        },
    )

    # 3. 최대 질문 수 초과 시 면접 종료
    if current_question_number >= MAX_QUESTIONS:
        await db["interviews"].update_one(
            {"_id": request.session_id},
            {"$set": {"status": "finished", "finished_at": now}},
        )
        return AnswerResponse(is_finished=True)

    # 4. Gemini API 호출 → 꼬리질문 생성
    #    대화 이력을 Gemini history 형식으로 변환
    history = []
    for q in questions:
        history.append({"role": "model", "parts": [q["question_content"]]})
        if q.get("answer"):
            history.append({"role": "user", "parts": [q["answer"]["answer_content"]]})

    # 세션의 system_prompt 재생성 (Gemini는 대화 상태를 저장하지 않음)
    system_prompt = build_system_prompt(
        job_role=doc["position"],
        tech_stack=doc["tech_stack"],
        experience_years=doc["career_years"],
    )

    model = get_client()
    chat = model.start_chat(history=history)
    response = chat.send_message(request.answer_content)
    follow_up_question = response.text.strip()

    # 5. 꼬리질문을 새 Question으로 MongoDB에 저장
    new_question = Question(
        question_number=current_question_number + 1,
        question_content=follow_up_question,
        category="기술",
        expected_duration_seconds=120,
        created_at=now,
        model_answer="",
        question_keywords=[],
    )

    await db["interviews"].update_one(
        {"_id": request.session_id},
        {"$push": {"questions": new_question.model_dump()}},
    )

    return AnswerResponse(follow_up_question=follow_up_question)

    # TODO: 세션에서 대화 이력 조회
    # TODO: Gemini API 호출하여 꼬리 질문 생성
    # TODO: 답변 및 태도 점수를 MongoDB에 저장
    #raise NotImplementedError
