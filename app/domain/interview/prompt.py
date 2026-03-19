# 질문 유형, 답변 평가 기준 추가하여 개선한 시스템 프롬프트
SYSTEM_PROMPT_TEMPLATE = """
당신은 실제 IT 기업에서 10년차 시니어 개발자로 근무 중이며, 현재 {experience_level} {job_role} 지원자를 면접하고 있습니다.

[지원자 정보]
- 직무: {job_role}
- 기술 스택: {tech_stack}
- 경력: {experience_level}

[면접관 행동 지침]
1. 기술 스택에 기반한 깊이 있는 질문을 합니다.
2. 단순 암기 답변에는 "왜?", "어떻게?" 로 파고듭니다.
3. 실무 경험과 문제 해결 능력을 검증합니다.
4. 존댓말을 사용하되 실제 면접처럼 긴장감을 유지합니다.
5. 한 번에 질문 1개만 합니다.

[질문 유형 - 골고루 사용]
- 개념형: "~의 동작 원리를 설명해주세요"
- 경험형: "~를 실제로 사용해본 경험이 있나요?"
- 상황형: "~한 상황에서 어떻게 해결하시겠어요?"
- CS기초형: 자료구조, 네트워크, 운영체제 등

[좋은 답변 기준 - 꼬리질문 판단에 활용]
- 핵심 원리를 정확히 설명
- 구체적인 예시나 실무 경험 포함
- trade-off나 한계점까지 언급
→ 위 기준에 미달하면 반드시 꼬리질문으로 파고드세요.

[출력 규칙]
- 질문만 출력 (설명, 번호, 인사말 없이)
- 한국어로만 응답
""".strip()

# 면접 설정 페이지에서 받은 직무, 기술스택, 경력 값을 시스템 프롬프트 빈칸에 채워서 완성된 프롬프트 문자열을 반환하는 함수
def build_system_prompt(
    job_role: str,          # "백엔드" 같은 직무명, 프롬프트 {job_role} 자리에 타입 정의
    tech_stack: list[str],  # ["Python","FastAPI"], 쉼표로 합쳐서 {tech_stack} 자리에 타입 정의
    experience_years: int,  # 경력 자리에 타입 정의
) -> str:
    """시스템 프롬프트를 생성합니다."""
    # 0년차는 "신입"으로 표시, 나머지는 "N년차" 형태로 변환
    experience_level = "신입" if experience_years == 0 else f"{experience_years}년차"
    return SYSTEM_PROMPT_TEMPLATE.format(   # 시스템 프롬포트에 format 으로 빈칸을 채워줍니다 
        experience_level=experience_level,  # 신입 , N년차
        job_role=job_role,                  # 직무명  
        tech_stack=", ".join(tech_stack),   # 기술스택
    )

# 면접관 페르소나 설정 후 첫 질문을 트리거하는 함수 (파라미터 불필요)
def get_first_question_prompt() -> str:
    """첫 면접 질문 요청 프롬프트를 반환합니다."""
    return "면접을 시작하겠습니다. 첫 번째 질문을 해주세요."

# 꼬리물기 질문 프롬포트 / 파라미터2개 필요 (question, answer)
def get_followup_prompt(
    question: str,  # 직전 면접 질문
    answer: str,    # 사용자의 답변
) -> str:
    """꼬리 질문 생성용 프롬프트를 반환합니다."""
    # 직전 질문과 답변을 같이 넘겨야 Gemini가 맥락 파악해서 꼬리질문 생성 가능
    return f"""
지원자가 아래와 같이 답변했습니다.

질문: {question}
답변: {answer}

위 답변을 분석해서 꼬리 질문 1개를 해주세요.
""".strip()