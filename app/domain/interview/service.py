import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from google.genai import types

from app.config import KST
from app.database import get_database
from app.domain.interview.models import Answer, InterviewDocument, Question
from app.domain.interview.prompt import (
    INTERVIEW_INTRO_MESSAGE,
    get_first_question_prompt,
    get_followup_prompt,
    get_model_answer_prompt,
)
from app.domain.interview.schema import (
    AnswerRequest,
    AnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.services.gemini import ask_question, create_chat_session

# 세션이 시작되면 첫 시작 문구가 뜨고, 첫 질문이 생성되어 뜬다.
# 그러면 내가 답변하고 답변한 시간이 기록된다. 그리고 다시 꼬리질문이 생성되어 뜬다.
# 그러면 꼬리에 대한 답을 하고... 최대 질문수에 도달하면 음성인식이 멈추고 면접 한 세션이 종료된다.
MAX_QUESTIONS = 5
# 면접 세션을 생성하고 첫 질문을 반환한다.
async def start_interview(request: InterviewStartRequest, user_id: str) -> InterviewStartResponse:
    """면접 세션을 생성하고 첫 질문을 반환합니다."""
    # Gemini API 호출하여 첫 질문 생성

    # 2. Gemini API 호출 → 첫 질문 생성(model 이 질문)
    chat = await create_chat_session(
        job_role=request.job_role,
        tech_stack=request.tech_stack,
        experience_years=request.experience_years)

    first_question = await ask_question(chat, get_first_question_prompt())
    model_answer_first = await ask_question(chat, get_model_answer_prompt(first_question))

    # 3. 세션 id 발급, document 생성
    session_id = str(uuid.uuid4())
    now = datetime.now(KST)

    document = InterviewDocument(
        user_id=user_id,   # router에서 받은 실제 user_id 사용
        position=request.job_role,
        tech_stack=request.tech_stack,
        career_years=request.experience_years,
        questions=[
            Question(
                question_number=1,
                question_content=first_question,
                category="기술",
                expected_duration_seconds=60, # 시간 1분으로 정함
                created_at=now,
                model_answer=model_answer_first,      # 추후 Gemini로 모범답안 생성 가능
                question_keywords=[],
            )
        ],
        status="in_progress",
        created_at=now,
    )
    # 세션 정보를 MongoDB에 저장
    db = get_database()
    await db["interviews"].insert_one(
        {**document.model_dump(), "_id": session_id}
    )

    # 4. 응답 반환
    return InterviewStartResponse(
        session_id=session_id,
        intro_message=INTERVIEW_INTRO_MESSAGE,
        question=first_question,
    )



#답변을 분석하고 꼬리 질문을 생성한다.
async def submit_answer(request: AnswerRequest, user_id: str) -> AnswerResponse:
    """답변을 분석하고 꼬리 질문을 생성합니다."""
    db = get_database()
    now = datetime.now(KST)

    # 1. MongoDB에서 세션 조회
    doc = await db["interviews"].find_one({"_id": request.session_id})
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"세션을 찾을 수 없습니다: {request.session_id}",
        )
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="본인의 면접 세션만 접근할 수 있습니다.")
    if doc.get("status") != "in_progress":
        raise HTTPException(status_code=400, detail="이미 종료된 면접입니다.")

    questions: list[dict] = doc.get("questions", [])
    current_question_number = len(questions)  # 현재까지 질문 수

    # 2. 현재 질문에 답변 저장

    # 현재 질문의 created_at = 사용자가 질문을 받은 시점 = 답변 시작 시점
    question_created_at = questions[current_question_number - 1]["created_at"]
    if isinstance(question_created_at, datetime):
        started_at = question_created_at
    else:
        started_at = datetime.fromisoformat(str(question_created_at))
    # MongoDB에서 읽어온 naive datetime에 KST 부여
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc).astimezone(KST)
    ended_at = now
    duration_seconds = request.duration_seconds if request.duration_seconds is not None else int((ended_at - started_at).total_seconds())

    answer = Answer(
        answer_content=request.answer_content,
        stt_raw_text=request.stt_raw_text,
        started_at=started_at,   # 백엔드에서 현재 시간으로 처리
        ended_at=ended_at,
        duration_seconds=duration_seconds,
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
        update_fields = {"status": "finished", "finished_at": now}
        if request.eye_contact is not None:
            update_fields["eye_contact"] = request.eye_contact
        if request.posture_safety_rate is not None:
            update_fields["posture_safety_rate"] = request.posture_safety_rate

        await db["interviews"].update_one(
            {"_id": request.session_id},
            {"$set": update_fields},
        )
        return AnswerResponse(is_finished=True)

    # 4. Gemini API 호출 → 꼬리질문 생성
    #    대화 이력을 Gemini history 형식으로 변환
    history = []
    for q in questions:
        history.append(types.Content(
            role="model",
            parts=[types.Part(text=q["question_content"])]
        ))
        if q.get("answer"):
            history.append(types.Content(
                role="user",
                parts=[types.Part(text=q["answer"]["answer_content"])]
            ))

    # 세션의 system_prompt 재생성 (Gemini는 대화 상태를 저장하지 않음)

    chat = await create_chat_session(job_role=doc["position"],
        tech_stack=doc["tech_stack"],
        experience_years=doc["career_years"],
        history=history)

    current_question = questions[current_question_number - 1]["question_content"]

    follow_up_question = await ask_question(
        chat,
        get_followup_prompt(current_question, request.answer_content)
    )
    model_answer_followup = await ask_question(chat, get_model_answer_prompt(follow_up_question))

    # 5. 꼬리질문을 새 Question으로 MongoDB에 저장
    new_question = Question(
        question_number=current_question_number + 1,
        question_content=follow_up_question,
        category="기술",
        expected_duration_seconds=60, #시간 1분으로 정함
        created_at=now,
        model_answer=model_answer_followup,
        question_keywords=[],
    )

    await db["interviews"].update_one(
        {"_id": request.session_id},
        {"$push": {"questions": new_question.model_dump()}},
    )

    return AnswerResponse(follow_up_question=follow_up_question)


