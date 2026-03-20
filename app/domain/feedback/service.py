from bson import ObjectId

from app.domain.feedback.schema import FeedbackRequest, FeedbackResponse, QuestionFeedbackResponse, PostureSummaryResponse
from app.domain.feedback.models import AiFeedback, PostureSummary, FeedbackDocument
from app.domain.interview.models import InterviewDocument
from app.database import get_database


# - router 에서 쓰일 함수 3개
# 피드백 생성 메인 함수
async def create_feedback(session_id: str) -> FeedbackResponse:
    # 1. 면접 데이터 조회
    # 2. AI 피드백 생성 (논리/기술점수, 강점/개선점, 총괄피드백)
    # 3. 자세 데이터 가공
    # 4. DB 저장
    # 5. 응답 변환
    pass

# 피드백 결과 조회 (feedback.html)
async def get_feedback(interview_id: str) -> FeedbackResponse:
    pass

# 히스토리 목록 조회 (history.html)
async def get_history(user_id: str) -> list[FeedbackResponse]:
    pass



# - 여기서만 쓰이는 내부 함수들 5개
# 면접 데이터들 가져오기
async def _get_interview(session_id: str) -> InterviewDocument:
    db = get_database()
    doc = await db["interviews"].find_one({"_id": ObjectId(session_id)})
    return InterviewDocument(**doc) # **: 딕셔너리를 풀어서 인자로 전달

# gemini 여기서 한번 호출해서 필요한거 다 받기
async def _generate_ai_feedback(interview) -> AiFeedback:
    pass
    # technical_score
    # logical_score
    # strengths_improvements
    # overall_feedback

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
    result = await db["feedback"].insert_one(feedback.model_dump()) # model_dump: mongo db라서 딕셔너리로 변환
    return str(result.inserted_id) # mongo db id 이상하게 생겨서 str로 변환 필요