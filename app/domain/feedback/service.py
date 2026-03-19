from app.domain.feedback.schema import FeedbackRequest, FeedbackResponse
from app.domain.feedback.models import AiFeedback, PostureSummary, FeedbackDocument

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
async def _get_interview(session_id: str):
    pass
    # 모범답안 interview에 있으니까 잊지말고 가져오기

# gemini 여기서 한번 호출해서 필요한거 다 받기
async def _generate_ai_feedback(interview) -> AiFeedback:
    pass
    # technical_score
    # logical_score
    # strengths_improvements
    # overall_feedback

# 자세/태도 데이터 받은거 가공하기 (=> 태도 점수)
def _process_posture(interview) -> PostureSummary:
    pass

# DB 데이터 -> 응답 변환
def _to_response(doc: FeedbackDocument) -> FeedbackResponse:
    pass
    # score_graph

# mongo db에 피드백 저장
async def _save_feedback(feedback: FeedbackDocument) -> str:
    pass
    # mongo db에서 document 저장하면 id 이상하게 생겨서 str로 변환 필요함