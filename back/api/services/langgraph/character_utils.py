# 등장인물 처리 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import difflib
import re
import google.generativeai as genai
import os
from typing import List
from .parsing_utils import normalize_name


# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------------------------------------------------------------
# 통합 캐릭터 처리 (성능 최적화: 3개 함수 → 1개 함수)
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 기존 3개 함수(extract_new_characters, filter_significant_characters, get_character_description)를 
#       하나로 통합하여 Gemini API 호출을 1회로 축소 (성능 최적화)
# 마지막 수정일: 2025-06-16
def extract_and_describe(text: str, user_input: str, known_names: list[str], age: int) -> dict:
    system_instruction = (
        f"You are a professional Korean children's story writer for kids aged {age}.\n"
        "Your task is to analyze a story paragraph and extract ONLY new, meaningful characters.\n\n"
        
        "Character Extraction Rules:\n"
        "1. ONLY extract characters who actively appear, speak, or perform actions\n"
        "2. EXCLUDE abstract concepts, metaphors, locations, or symbolic entities\n"
        "3. EXCLUDE meaningless sounds or animal noises (e.g., 'neigh', 'woof')\n"
        "4. ONLY include characters who are PERSONIFIED and visibly present\n"
        "5. Filter to characters who have MEANINGFUL impact on the story\n\n"
        
        "Character Description Rules:\n"
        "1. Include: gender, hair/fur color, eye color, age, species (human/animal/etc)\n"
        "2. Be specific and child-appropriate, avoid vague terms like 'unknown'\n"
        "3. For animals: use Korean nickname-style names\n"
        "4. For humans: use proper Korean names\n"
        "5. Each character must have a unique name\n\n"
        
        f"Known Characters (DO NOT include): {', '.join(known_names)}\n\n"
        
        "Output ONLY valid JSON format. No explanations."
    )

    user_request = (
        f"[Story Paragraph]\n{text}\n\n"
        f"[User Input]\n{user_input}\n\n"
        
        "Analyze the text and extract new meaningful characters with descriptions.\n\n"
        
        "Output format (JSON only):\n"
        '{\n'
        '  "new_characters": [\n'
        '    {"name": "name1", "description": "수컷, 갈색 털, 검은 눈동자, 3세, 강아지"},\n'
        '    {"name": "name2", "description": "수컷, 파란 털, 초록 눈, 4세, 고양이"}\n'
        '  ]\n'
        '}\n\n'
        
        "Rules:\n"
        "- Return empty array if no meaningful new characters found\n"
        "- Each description format: 'gender, hair/fur color, eye color, age, species'\n"
        "- Use Korean only, no English\n"
        "- Must be valid JSON"
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': 'Understood. I will extract meaningful new characters and provide descriptions in JSON format.'}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    try:
        response = model.generate_content(contents)
        response_text = response.text.strip()
        
        if debug:
            print("\n" + "-" * 40)
            print("[ExtractAndDescribe] DEBUG LOG")
            print("-" * 40)
            print(f"Known Names: {known_names}")
            print(f"Raw Response Text:\n{response_text}")
            print("-" * 40 + "\n")

        # JSON 추출 및 파싱
        import json
        
        # JSON 부분만 추출
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_content = response_text[json_start:json_end].strip()
        elif "{" in response_text and "}" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_content = response_text[start:end]
        else:
            if debug:
                print("[ExtractAndDescribe] No JSON found in response")
            return {"new_characters": []}
            
        result = json.loads(json_content)
        characters = result.get("new_characters", [])
        
        # 유효성 검사 및 필터링
        filtered_characters = []
        for char in characters:
            name = char.get("name", "").strip()
            desc = char.get("description", "").strip()
            
            # 한글 이름 및 중복 검사
            if (
                re.fullmatch(r"[가-힣]{2,6}", name) and 
                name not in known_names and 
                not is_similar_name(name, known_names) and
                desc
            ):
                filtered_characters.append({"name": name, "description": desc})
        
        if debug:
            print(f"[ExtractAndDescribe] Filtered Result: {filtered_characters}")
            
        return {"new_characters": filtered_characters}
        
    except Exception as e:
        if debug:
            print(f"[ExtractAndDescribe] Error: {e}")
        return {"new_characters": []}



# ------------------------------------------------------------------------------------------
# 이름 유사도 및 중복 검사
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 이름에 대한 중복 여부 체크
# 마지막 수정일: 2025-06-12
def is_similar_name(name: str, known_names: list[str], threshold: float = 0.8) -> bool:
    name_norm = normalize_name(name)
    for kn in known_names:
        ratio = difflib.SequenceMatcher(None, name_norm, normalize_name(kn)).ratio()
        if debug:
            print(f"[SimilarityCheck] {name_norm} vs {kn} → {ratio:.2f}")
        if ratio >= threshold:
            return True
    return False


# 작성자: 최준혁
# 기능: 이름과 전체 프로필 유사도를 함께 고려해 중복 인물 여부 판단
# 마지막 수정일: 2025-06-15
def is_duplicate_character(new_name: str, new_desc: str, existing_lines: list[str], threshold: float = 0.8) -> bool:
    new_name_norm = normalize_name(new_name)
    new_desc_clean = re.sub(r"^\d+\.\s*", "", new_desc)

    for line in existing_lines:
        line_clean = re.sub(r"^\d+\.\s*", "", line)
        if ":" not in line_clean:
            continue
        existing_name, existing_profile = map(str.strip, line_clean.split(":", 1))
        name_sim = difflib.SequenceMatcher(None, new_name_norm, normalize_name(existing_name)).ratio()
        profile_sim = difflib.SequenceMatcher(None, new_desc_clean, existing_profile).ratio()

        if name_sim >= threshold and profile_sim >= 0.75:
            if debug:
                print(f"[중복감지] {new_name} ≈ {existing_name} (이름: {name_sim:.2f}, 프로필: {profile_sim:.2f})")
            return True
    return False

# 작성자: 최준혁
# 기능: 이름에 대한 유사도 측정
# 마지막 수정일: 2025-06-15
def get_similar_name(name: str, known_names: list[str], threshold: float = 0.8) -> str | None:
    name_norm = normalize_name(name)
    best_match = None
    best_ratio = 0.0
    for kn in known_names:
        ratio = difflib.SequenceMatcher(None, name_norm, normalize_name(kn)).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_match = kn
            best_ratio = ratio
    if debug and best_match:
        print(f"[MatchFound] {name} → {best_match} (ratio {best_ratio:.2f})")
    return best_match















# ------------------------------------------------------------------------------------------
# 인물 추출 및 필터링 (레거시 - 호환성용) 아래의 코드는 현재 사용하지 않습니다.
# ------------------------------------------------------------------------------------------

# 레거시 경고: 아래 함수들은 성능상 이유로 비추천
# 대신 extract_and_describe() 사용 권장

# 작성자: 최준혁
# 기능: 문단에서 등장하는 인물들 중 '스토리 전개에 의미 있는 영향을 준 인물'만 골라서 이름만 리스트로 출력하는 함수
# 마지막 수정일: 2025-06-15
# 레거시: extract_and_describe() 사용 권장
def filter_significant_characters(paragraph: str, candidates: list[str], user_input: str = "") -> list[str]:
    prompt = (
        "다음은 동화의 한 문단입니다. 이 문단에서 등장하는 인물들 중 "
        "'스토리 전개에 의미 있는 영향을 준 인물'만 골라서 이름만 리스트로 출력해주세요.\n\n"
        f"[문단 내용]\n{paragraph}\n\n"
        f"[사용자 입력]\n{user_input}\n\n"
        f"[후보 인물 리스트]: {', '.join(candidates)}\n\n"
        "→ 반드시 인물 이름만 콤마(,)로 구분된 한 줄로 출력해주세요. 중요한 인물이 없다면 '없음'이라고 하세요."
    )

    response = model.generate_content(prompt)
    line = response.text.strip()
    if line.lower().startswith("없음"):
        return []
    return [name.strip() for name in line.split(",") if name.strip()]

# 작성자: 최준혁
# 기능: 문단에서 새롭게 등장한 인물 이름을 추출하는 함수
# 마지막 수정일: 2025-06-12
# 레거시: extract_and_describe() 사용 권장
def extract_new_characters(text: str, known_names: list[str]) -> list[str]:
    system_instruction = (
        "You are a smart assistant helping identify characters in a Korean children's story.\n"
        "Your task is to extract ONLY the proper names of characters who actively appear, speak, or perform actions in the paragraph.\n"
        "Exclude any beings or terms that only refer to abstract concepts, metaphors, locations, or symbolic entities (like 어비스, 꿈, 세계, 별 등).\n"
        "Only include character names who are PERSONIFIED and visibly present in the scene.\n"
        "**Do NOT include meaningless interjections or animal sounds (e.g., \"neigh\", \"woof\", \"meow\") as character names.**\n"
        f"Do NOT include already known characters: {', '.join(known_names)}\n"
        "Return names only in Korean, separated by commas, in one line. No description."
    )

    user_request = (
        f"[Paragraph]\n{text}\n\n"
        "→ Output format: 피요, 포코\n"
        "→ Return only names, comma-separated. No bullets, no markdown, no explanations."
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': 'Understood. I will extract new character names only.'}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    response_text = response.text.strip()

    if debug:
        print("\n" + "-" * 40)
        print("[ExtractCharacters] DEBUG LOG")
        print("-" * 40)
        print(f"Known Names:\n{known_names}")
        print(f"Raw Response Text:\n{response_text}")
        print("-" * 40 + "\n")

    # 필터 완화: 비어 있으면 종료
    if not response_text:
        return []

    # 쉼표 없는 단일 텍스트 대응
    if "," not in response_text and len(response_text) <= 4:
        candidates = [response_text.strip()]
    else:
        candidates = [n.strip() for n in response_text.split(",") if n.strip()]

    # 한글 이름만 필터
    valid_names = [n for n in candidates if re.fullmatch(r"[가-힣]{2,6}", n)]

    # 중복 및 유사도 제거
    new_names = []
    for name in valid_names:
        if name not in known_names and not is_similar_name(name, known_names):
            new_names.append(name)

    if debug:
        print("[ExtractCharacters Response Filtered]", new_names)

    return new_names


# ------------------------------------------------------------------------------------------
# 인물 프로필 생성 (레거시 - 호환성용)
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 사용자의 입력으로 새롭게 추가되는 등장인물의 특징을 추정하는 함수
# 마지막 수정일: 2025-06-13
# 레거시: extract_and_describe() 사용 권장
def get_character_description(name: str, context: str, user_input: str, age: int, known_characters: list[str]) -> str:
    def extract_name_from_line(line):
        parts = line.split(":", 1)
        return parts[0].split(".", 1)[-1].strip() if len(parts) > 1 else ""

    existing_names = [extract_name_from_line(line) for line in known_characters]

    if name in existing_names or is_similar_name(name, existing_names):
        print(f"[중복 인물 감지] '{name}'은 이미 존재하는 인물로 판단 → description 생략")
        return None

    next_number = len(known_characters) + 1

    # system role instruction
    system_instruction = (
        f"You are a professional children's story writer for Korean kids aged {age}.\n"
        f"Based on the story context and user input, your job is to infer accurate and specific characteristics of a newly introduced character.\n"
        f"Your description must include: gender, hair color, eye color, age, and species (such as human, animal, fairy, etc).\n"
        f"Avoid vague expressions like 'unknown'. Be specific and child-appropriate.\n"
        f"The response should be in Korean and match the format provided."
    )

    # user message prompt
    user_request = (
        f"[Character to Describe]\n{name}\n\n"
        f"[Format Example]\n"
        f"{next_number}. {name} : 성별, 머리색, 눈동자색, 나이, 종족\n"
        f"예시:\n"
        f"1. 민준 : 남성, 검은색, 파란색, 12세, 인간\n"
        f"2. 뭉치 : 수컷, 하얀 털, 검은 눈동자, 3세, 강아지\n\n"
        f"[Story Context]\n{context}\n\n"
        f"[User Input]\n{user_input}\n\n"
        f"[Existing Characters]\n{', '.join(known_characters)}\n\n"
        f"→ Do NOT repeat or rename any existing characters.\n"
        f"→ Return only one line. No explanations, no extra formatting.\n"
        f"→ Avoid vague labels like \"unknown\" or \"none\" — always infer a likely gender, age, and species based on the context.\n"
        f"→ Output must be written in Korean only."
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': "Understood. I will describe the new character in Korean, following the format."}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    first_line = response.text.strip().splitlines()[0]

    # 정규표현식으로 형식 맞추기: "번호. 이름 : 성별, 머리색, 눈동자색, 나이, 종족"까지만 유지
    cleaned_line = re.match(r"^\d+\.\s*[^:]+:\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+", first_line)
    result = cleaned_line.group(0) if cleaned_line else first_line.split(".")[0] + ". " + first_line.split(":", 1)[-1].strip()

    print("[Character Desc]", result)
    return result


# ------------------------------------------------------------------------------------------
# 인물 목록 관리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 등장인물 리스트에서 번호를 1부터 다시 매김
# 마지막 수정일: 2025-06-15
def renumber_characters(character_lines: list[str]) -> list[str]:
    result = []
    for idx, line in enumerate(character_lines, 1):
        # 기존 번호 제거 ("1. 라이카 : ..." → "라이카 : ...")
        line_clean = re.sub(r"^\d+\.\s*", "", line).strip()
        result.append(f"{idx}. {line_clean}")
    return result
