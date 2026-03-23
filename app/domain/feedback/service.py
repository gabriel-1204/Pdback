import json
import re

from bson import ObjectId

from app.domain.feedback.schema import (
    FeedbackResponse, QuestionFeedbackResponse,
    PostureSummaryResponse)
from app.domain.feedback.models import (
    AiFeedback, PostureSummary,
    FeedbackDocument, QuestionFeedback)
from app.domain.interview.models import InterviewDocument
from app.domain.feedback.prompt import get_feedback_prompt
from app.services.gemini import get_client
from app.database import get_database


# === router.py 함수 3개
# 피드백 생성 메인 함수
async def create_feedback(session_id: str) -> FeedbackResponse:

    interview = await _get_interview(session_id)          # 면접 데이터
    ai_feedback = await _generate_ai_feedback(interview)  # ai 피드백
    posture_summary = _process_posture(interview)         # 자세/태도 데이터

    # DB에 저장할 문서 생성
    feedback_doc = FeedbackDocument(
        interview_id=session_id,
        user_id=interview.user_id,
        ai_feedback=ai_feedback,
        posture_summary=posture_summary,
    )

    await _save_feedback(feedback_doc)             # DB에 저장
    return _to_response(feedback_doc, interview)   # 응답 형태로 변환


# 피드백 결과 조회 (feedback.html)
async def get_feedback(interview_id: str) -> FeedbackResponse:
    db = get_database()

    # feedbacks 컬렉션에서 면접 id로 조회
    doc = await db["feedbacks"].find_one({"interview_id": interview_id})
    feedback_doc = FeedbackDocument(**doc)          # 피드백 데이터
    interview = await _get_interview(interview_id)  # 면접 데이터 (schema)

    return _to_response(feedback_doc, interview)


# 히스토리 목록 조회 (history.html)
async def get_history(user_id: str) -> list[FeedbackResponse]:
    db = get_database()

    # feedbacks 컬렉션에서 유저 id로 모든 피드백 조회
    # (find는 포인터기 때문에 to_list로 실제 데이터 꺼내기/ length: 몇개까지 가져올지)
    docs = await db["feedbacks"].find({"user_id": user_id}).to_list(length=None)

    result = []
    for doc in docs:
        feedback_doc = FeedbackDocument(**doc)
        interview = await _get_interview(feedback_doc.interview_id)
        result.append(_to_response(feedback_doc, interview))

    return result



# === service.py 내부 함수 5개
# 면접 데이터들 가져오기
async def _get_interview(session_id: str) -> InterviewDocument:
    db = get_database()
    doc = await db["interviews"].find_one({"_id": ObjectId(session_id)})
    return InterviewDocument(**doc) # **: 딕셔너리를 풀어서 인자로 전달


# gemini 여기서 한번 호출해서 필요한거 다 받기
async def _generate_ai_feedback(interview: InterviewDocument) -> AiFeedback:
    # interview에서 질문/답변 목록 추출
    questions = [q.question_content for q in interview.questions]
    answers = []
    for q in interview.questions:
        if q.answer:                      
            answers.append(q.answer.answer_content)
        else:  
            answers.append("")

    # 피드백 프롬프트 생성
    prompt = get_feedback_prompt(
        questions=questions,
        answers=answers,
        job_role=interview.position,
        experience_years=interview.career_years,
    )

    # Gemini 호출(채팅 세션 불필요, 피드백 생성은 대화형이 아니라 분석용이라 단발성)
    client = get_client()
    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt,
    )

    # gemini 응답이 마크다운 껍데기에 싸여서 나오는 경우 대비하여 파싱 코드
    # 파싱: 텍스트를 프로그램이 쓸 수 있는 구조로 변환하는것
    raw = response.text.strip()                 # gemini 응답 텍스트 꺼내기
    raw = re.sub(r"^```(?:json)?\s*", "", raw)  # 앞쪽 ```json -> 빈 문자열로 대체
    raw = re.sub(r"\s*```$", "", raw).strip()   # 뒤쪽 ``` -> 빈 문자열로 대체
    data = json.loads(raw)                      # 'json 문자열' -> {python 딕셔너리}

    question_feedbacks = []
    # qf: 리스트 원소 하나하나/ "question_feedbacks": gemini 응답 json 키 이름, db 필드 이름
    for qf in data["question_feedbacks"]:
        question_feedbacks.append(
            QuestionFeedback(
                question_number=qf["question_number"],
                score=qf["score"],
                comment=qf["comment"],
            )
        )

    return AiFeedback(
        interview_score=data["interview_score"],
        technical_score=data["technical_score"],
        logic_score=data["logic_score"],
        keyword_score=data["keyword_score"],
        interview_comment=data["interview_comment"],
        strengths=data["strengths"],
        improvements=data["improvements"],
        question_feedbacks=question_feedbacks,
    )


# 자세/태도 데이터 받은거 피드백으로 가공
def _process_posture(interview) -> PostureSummary:
    posture_score = interview.posture_safety_rate
    eyes_score = interview.eye_contact
    attitude_score = round(eyes_score * 0.4 + posture_score * 0.6, 1)

    # 테스트 후 숫자 변경, 조건문 범위 변경 가능성 있음/ 단계: 부족-> 보통-> 완벽
    if eyes_score >= 80 and posture_score >= 80: # 전부 80 이상. 모두 완벽!
        comment = "시선 처리와 자세 모두 안정적이었습니다. 면접 내내 자신감 있는 태도를 유지했습니다."
    elif eyes_score >= 80 and 60 <= posture_score < 80: # 시선 완벽/ 자세 보통
        comment = "시선 처리는 훌륭했습니다. 자세를 조금만 더 바르게 유지한다면 더욱 좋은 인상을 줄 수 있습니다."
    elif eyes_score >= 80 and posture_score < 60: # 시선 완벽/ 자세 부족    
        comment = "시선 처리는 좋았으나, 자세가 많이 흐트러졌습니다. 앉은 자세를 의식적으로 바르게 유지해보세요."
    elif 60 <= eyes_score < 80 and posture_score >= 80: # 시선 보통/ 자세 완벽
        comment = "자세는 훌륭했습니다. 카메라를 조금만 더 자주 응시한다면 더욱 자신감 있어 보일 것입니다."
    elif eyes_score < 60 and posture_score >= 80: # 시선 부족/ 자세 완벽        
        comment = "자세는 안정적이었으나, 카메라 응시가 많이 부족했습니다. 면접관(카메라)을 자주 바라보는 연습을 해보세요."
    elif eyes_score >= 60 and posture_score >= 60: # 시선 보통/ 자세 보통
        comment = "시선 처리와 자세 모두 나쁘지 않았습니다. 전반적으로 조금만 더 자신감 있게 임해보세요."
    elif 60 <= eyes_score < 80 and posture_score < 60: # 시선 보통/ 자세 부족
        comment = "자세가 특히 불안정했습니다. 앉은 자세를 의식적으로 바르게 유지해보세요."
    elif eyes_score < 60 and 60 <= posture_score < 80: # 시선 부족/ 자세 보통
        comment = "카메라 응시가 특히 부족했습니다. 면접관(카메라)을 자주 바라보는 연습을 해보세요."
    else: # 전부 60 미만. 모두 부족!
        comment = "시선 처리와 자세 모두 개선이 필요합니다. 카메라를 정면으로 응시하고 허리를 펴는 습관을 들여보세요."

    return PostureSummary(
        eyes_score=eyes_score,
        posture_score=posture_score,
        attitude_score=attitude_score,
        posture_comment=comment,
    )


# DB 데이터 -> 응답 변환
# 수정, 검토중
def _to_response(doc: FeedbackDocument, interview: InterviewDocument) -> FeedbackResponse:
    # question_number 기준으로 model_answer 매핑 딕셔너리 생성
    model_answers = {q.question_number: q.model_answer for q in interview.questions}
    question_contents = {q.question_number: q.question_content for q in interview.questions}
    answer_contents = {q.question_number: q.answer.answer_content for q in interview.questions if q.answer}

    question_feedbacks = [
        QuestionFeedbackResponse(
            question_number=qf.question_number,
            score=qf.score,
            comment=qf.comment,
            model_answer=model_answers.get(qf.question_number, ""),
            question_content=question_contents.get(qf.question_number, ""),
            answer_content=answer_contents.get(qf.question_number, ""),
        )
        for qf in doc.ai_feedback.question_feedbacks
    ]

    posture_summary = PostureSummaryResponse(
        eyes_score=doc.posture_summary.eyes_score,
        posture_score=doc.posture_summary.posture_score,
        attitude_score=doc.posture_summary.attitude_score,
        posture_comment=doc.posture_summary.posture_comment,
    )

    return FeedbackResponse(
        interview_score=doc.ai_feedback.interview_score,
        technical_score=doc.ai_feedback.technical_score,
        logic_score=doc.ai_feedback.logic_score,
        keyword_score=doc.ai_feedback.keyword_score,
        interview_comment=doc.ai_feedback.interview_comment,
        strengths=doc.ai_feedback.strengths,
        improvements=doc.ai_feedback.improvements,
        question_feedbacks=question_feedbacks,
        posture_summary=posture_summary,
    )


# mongo db에 피드백 저장
async def _save_feedback(feedback: FeedbackDocument) -> str:
    db = get_database()
    # model_dump: mongo db라서 딕셔너리로 변환
    result = await db["feedbacks"].insert_one(feedback.model_dump())
    return str(result.inserted_id) # mongo db id 이상하게 생겨서 str로 변환 필요
