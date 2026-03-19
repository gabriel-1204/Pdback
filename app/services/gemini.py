import google.generativeai as genai

from app.config import settings


def configure_gemini():
    """Gemini API 키를 설정합니다."""
    genai.configure(api_key=settings.GEMINI_API_KEY)


def get_model(model_name: str = "gemini-2.0-flash") -> genai.GenerativeModel:
    """Gemini 모델 인스턴스를 반환."""
    return genai.GenerativeModel(model_name)


# 면접관 페르소나 설정 후 Gemini 대화 세션을 생성하는 함수
def create_chat_session(
    job_role: str,
    tech_stack: list[str],
    experience_years: int,
) -> genai.ChatSession:
    """면접관 페르소나가 설정된 Gemini 대화 세션 생성"""
    # prompt.py 에서 시스템 프롬프트 가져오기
    from app.domain.interview.prompt import build_system_prompt

    # API 키 설정
    configure_gemini()

    # 시스템 프롬프트 완성 / 시스템 프롬포트에 빈칸에 내용을 삽입함
    system_prompt = build_system_prompt(job_role, tech_stack, experience_years)

    # llm 모델 지정
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",          # 사용할 모델
        system_instruction=system_prompt,       # llm 에게 시스템 프롬포트 주입
    )

    # 대화 세션 시작 (history[]에 대화 내용이 저장됨)
    return model.start_chat(history=[])


# Gemini한테 말 걸고 대답 받아오는 함수
async def ask_question(
    chat: genai.ChatSession,  # create_chat_session()으로 만든 대화 세션
    prompt: str,              # Gemini한테 보낼 메시지
) -> str:                     # Gemini 응답 문자열 반환
    """Gemini에게 질문을 요청하고 응답을 반환합니다."""
    response = await chat.send_message_async(prompt) # Gemini에게 문자열로 보냄
    return response.text.strip()                     # Gemini가 그걸 기반으로 답변을함