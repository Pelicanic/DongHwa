# 텍스트 파싱 및 정규화 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import re
from typing import Tuple, List


# ------------------------------------------------------------------------------------------
# 문자열 파싱 함수
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: Gemini의 응답을 파싱하여 문장, 질문, 선택지로 분리
# 마지막 수정일: 2025-06-10
def extract_choice(text: str, paragraph_no: int = None) -> Tuple[str, str, List[str]]:
    # 에필로그 처리: [문장]만 있을 수 있음
    if paragraph_no == 10:
        # '[문장]' 태그까지 지우고 순수한 문장만 반환
        match = re.search(r"\[문장\](.*)", text, re.DOTALL)
        paragraph = match.group(1).strip() if match else text.strip()
        return paragraph, "", []
    
    # 기본 처리
    match = re.search(r"\[문장\](.*?)\[질문\](.*?)\[행동\](.*)", text, re.DOTALL)
    if not match:
        return text.strip(), "", []
    
    paragraph = match.group(1).strip()
    question = match.group(2).strip()
    actions_raw = match.group(3).strip()
    choices = [line.strip("-•*●· ") for line in actions_raw.split("\n") if line.strip()]
    return paragraph, question, choices



# ------------------------------------------------------------------------------------------
# 텍스트 정규화
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: extract_new_characters에서 사용하는 이름 정규화 함수
# 마지막 수정일: 2025-06-14
def normalize_name(name: str) -> str:
    name = re.sub(r"(님|씨|양|군|아저씨|형|누나|오빠|이모|삼촌|선생님)$", "", name)
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', name).lower()


# ------------------------------------------------------------------------------------------
# 입력 유형 검사
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 사용자 입력이 선택지만 포함되어 있는지 확인하는 함수
# 마지막 수정일: 2025-06-15
def is_choice_only(text: str) -> bool:
    lines = [line.strip() for line in text.strip().splitlines()]
    return all(re.match(r"^\d+\.\s", line) for line in lines if line)
