from google import genai
from google.genai import types
from google.genai.chats import AsyncChat

from app.config import settings
from app.domain.interview.prompt import build_system_prompt
# 클라이언트를 모듈 레벨에서 한 번만 생성 (함수 끝나도 안 닫힘)
# genai.Client거나 클라이언트가 없으면None(아직생성안됨) / 처음은 None으로 시작
_client: genai.Client | None = None


# 이함수는 글로벌로 _client를 가져오고 처음실행하는거면
# None 이니까 if 문으로 인해 None이 있냐?로 트루가 되서 ganai.Client로 
# api키를 불러오고 Api가 들어있는 Client를 외부로 반환
def get_client() -> genai.Client:
    """Gemini 클라이언트를 반환합니다."""
    global _client
    # 클라이언트가 없으면 새로 만들고, 있으면 기존 것 재사용
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


# 면접관 페르소나 설정 후 Gemini 대화 세션을 생성하는 함수
async def create_chat_session(
    job_role: str,          #직무
    tech_stack: list[str],  #기술 스택
    experience_years: int,  #경력
    history: list[types.Content] | None = None  # list[dict] → list[types.Content]
) -> AsyncChat:  # 반환 타입 추가
    """면접관 페르소나가 설정된 Gemini 대화 세션 생성"""
    history = history or []

    # get_client 함수 사용(API)
    client = get_client()
    # 위에서 불러온 직무명, 기술스택, 경력을 build_system_prompt
    # 빈칸에 삽입하여 system_prompt 변수 생성 
    system_prompt = build_system_prompt(job_role, tech_stack, experience_years)

    return client.aio.chats.create(             # 비동기 대화 세션 만듬
        model="gemini-3.1-flash-lite-preview",  # 사용할 LLM 모델
        history=history or [],
        config=types.GenerateContentConfig(     #LLM에게 역할 설정
            system_instruction=system_prompt,   #시스템 프롬포트 주입
            temperature=1.0,         # 답변 창의성 (0~1, 낮을수록 일관된 답변)
            max_output_tokens=500,   # 최대 답변 길이
        ),
    )


# Gemini한테 말 걸고 대답 받아오는 함수
async def ask_question(
    chat: AsyncChat,
    prompt: str,    # Gemini한테 보낼 메시지
) -> str:
    """Gemini에게 질문을 요청하고 응답을 반환합니다."""
    # chat 세션을 통해 Gemini한테 메시지를 보내고 응답을 기다림.
    response = await chat.send_message(prompt)
    return response.text.strip() # Gemini 응답