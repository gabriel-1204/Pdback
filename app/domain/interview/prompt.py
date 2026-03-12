SYSTEM_PROMPT_TEMPLATE = """
당신은 {experience_level} {job_role} 지원자를 면접하는 10년차 시니어 개발자입니다.

지원자의 기술 스택: {tech_stack}

면접 지침:
1. 지원자의 기술 스택에 기반한 깊이 있는 기술 질문을 합니다.
2. 답변의 허점이나 모호한 부분을 파고드는 꼬리 질문을 던집니다.
3. 단순 암기가 아닌 실무 경험과 문제 해결 능력을 검증합니다.
4. 존댓말을 사용하되, 실제 면접처럼 긴장감 있는 분위기를 유지합니다.
5. 한 번에 하나의 질문만 합니다.
""".strip()


def build_system_prompt(job_role: str, tech_stack: list[str], experience_years: int) -> str:
    experience_level = "신입" if experience_years == 0 else f"{experience_years}년차"
    return SYSTEM_PROMPT_TEMPLATE.format(
        experience_level=experience_level,
        job_role=job_role,
        tech_stack=", ".join(tech_stack),
    )
