# feedbacks 컬렉션 필드
# interview_score   → 면접 종합 점수 (0~10)
# technical_score   → 기술 이해도 점수 (0~10)
# logic_score       → 논리적 전달력 점수 (0~10)
# keyword_score     → 핵심 키워드 포함도 점수 (0~10)
# interview_comment → 면접 총평 텍스트
# strengths         → 강점 목록 (배열)
# improvements      → 개선점 목록 (배열)
# question_feedbacks → 질문별 피드백 목록 (배열)

def get_feedback_prompt(
    questions: list[str],  # 면접에서 나온 질문 목록
    answers: list[str],    # 질문에 대응하는 답변 목록 (인덱스 순서 일치)
    job_role: str,         # 직무명 (경력 대비 평가 기준에 활용)
    experience_years: int, # 경력 (절대평가 기준에 활용)
) -> str:
    """면접 종합 피드백 생성용 프롬프트를 반환합니다."""
    # zip()으로 질문/답변을 짝지어서 하나의 텍스트로 합침
    qa_text = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_text += f"Q{i}. {q}\nA{i}. {a}\n\n"

    experience_level = "신입" if experience_years == 0 else f"{experience_years}년차"

    return f"""
당신은 {job_role} {experience_level} 지원자의 면접을 종합 평가하는 시니어 개발자입니다.

아래 면접 질문과 답변 전체를 분석해 종합 피드백을 작성해주세요.

{qa_text}

[채점 규칙 - 반드시 준수]
- 경력은 참고용이며 채점에 영향을 주지 않습니다
- 답변 내용만으로 절대평가합니다

[채점 기준 (0.0~10.0점)]

technical_score: 기술 이해도
  - 핵심 원리 언급 없음: 0.0~2.0점
  - 핵심 원리 언급했지만 부정확: 2.0~4.0점
  - 핵심 원리 정확히 설명: 4.0~6.0점
  - 핵심 원리 + 관련 개념 연결 설명: 6.0~8.0점
  - 핵심 원리 + 관련 개념 + 트레이드오프까지 설명: 8.0~10.0점

logic_score: 논리적 전달력
  - 결론 없이 두서없이 답변: 0.0~2.0점
  - 결론은 있지만 근거 없음: 2.0~4.0점
  - 결론 + 근거 제시: 4.0~6.0점
  - 결론 + 근거 + 구체적 사례 포함: 6.0~8.0점
  - 두괄식 + STAR 기법 + 수치/사례까지 포함: 8.0~10.0점

keyword_score: 핵심 키워드 포함도
  - 핵심 키워드 전혀 없음: 0.0~2.0점
  - 핵심 키워드 1개 포함: 2.0~4.0점
  - 핵심 키워드 2~3개 포함: 4.0~6.0점
  - 핵심 키워드 + 수치/정량적 표현 포함: 6.0~8.0점
  - 핵심 키워드 + 수치 + 실무 사례까지 포함: 8.0~10.0점

interview_score: 위 3개 점수의 평균값
  (technical_score + logic_score + keyword_score) / 3

반드시 아래 JSON 형식으로만 응답.
코드 블록(```) 없이 순수 JSON만 출력하세요.
아래는 형식 예시입니다. 숫자와 텍스트는 실제 평가 결과로 채우세요.
strengths 2~4개, improvements 2~4개, question_feedbacks 는 질문 개수만큼 작성하세요.

{{
  "interview_score": 0.0,
  "technical_score": 0.0,
  "logic_score": 0.0,
  "keyword_score": 0.0,
  "interview_comment": "총평을 여기에 작성",
  "strengths": ["강점1", "강점2", "강점3"],
  "improvements": ["개선점1", "개선점2"],
  "question_feedbacks": [
    {{"question_number": 1, "score": 0.0, "comment": "코멘트를 여기에 작성"}}
  ]
}}
""".strip()
