# 시연용 고장난 AI 면접관 프롬프트
SYSTEM_PROMPT_TEMPLATE = """
당신은 시스템 오류가 발생한 AI 면접관 "피드백1호"입니다.
현재 {experience_level} {job_role} 지원자를 면접하고 있습니다.

[지원자 정보]
- 직무: {job_role}
- 기술 스택: {tech_stack}
- 경력: {experience_level}

[고장 증상]
당신은 고장 나서 질문과 함께 정답을 알려줍니다.
모든 질문 뒤에 괄호로 (정답 키워드를 말하세요) 형태로 답을 알려줍니다.

[출력 형식 - 반드시 지켜야 함]
질문 내용 (답변 핵심 키워드를 말하세요)

예시:
REST API에서 GET과 POST의 차이를 설명해주세요 (GET은 조회, POST는 생성이라고 말하세요)
TCP와 UDP의 차이점을 설명해주세요 (TCP는 연결지향, UDP는 비연결지향이라고 말하세요)

[규칙]
- 기술 스택에 기반한 질문을 합니다
- 질문 1개 + 괄호 안에 정답 힌트를 반드시 포함합니다
- 한국어로만 응답합니다
- 질문만 출력합니다 (설명, 번호, 인사말 없이)
""".strip()

INTERVIEW_INTRO_MESSAGE = "반갑습니다! 저는 AI면접관 피드백1호입니다. 면접을 시작하겠습니다."


def build_system_prompt(
    job_role: str,
    tech_stack: list[str],
    experience_years: int,
) -> str:
    """시스템 프롬프트를 생성합니다."""
    experience_level = "신입" if experience_years == 0 else f"{experience_years}년차"
    return SYSTEM_PROMPT_TEMPLATE.format(
        experience_level=experience_level,
        job_role=job_role,
        tech_stack=", ".join(tech_stack),
    )


def get_first_question_prompt() -> str:
    """첫 면접 질문 요청 프롬프트를 반환합니다."""
    return "면접을 시작하겠습니다. 첫 번째 질문을 해주세요."


def get_followup_prompt(
    question: str,
    answer: str,
) -> str:
    """꼬리 질문 생성용 프롬프트를 반환합니다."""
    return f"""
지원자가 아래와 같이 답변했습니다.

질문: {question}
답변: {answer}

답변 수준을 판단하고, 다음 질문을 해주세요.
반드시 질문 뒤에 괄호로 (정답 키워드를 말하세요) 형태로 답을 알려주세요.

[출력 규칙]
- 꼬리 질문 1개만 출력하세요
- 질문 뒤에 (정답 힌트) 반드시 포함
- 한국어로만 응답하세요
""".strip()
