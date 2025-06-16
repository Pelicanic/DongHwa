# LangGraph 노드 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
import google.generativeai as genai
import difflib
import os
import re

from typing import Tuple, List
from api.models import Story, Storyparagraph, Paragraphversion, Paragraphqa
from django.utils import timezone
from api.services.vector_utils import search_similar_paragraphs
from api.services.vector_utils import index_paragraphs_to_faiss
from api.services.vector_utils import get_latest_paragraphs

# ------------------------------------------------------------------------------------------
# 디버깅
# ------------------------------------------------------------------------------------------

debug = True


# ------------------------------------------------------------------------------------------
# Gemini 초기화 및 모델 정의
# ------------------------------------------------------------------------------------------

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------------------------------------------------------------
# 패러그래프 생성 관련
# ------------------------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 주제/분위기 기반 4단계 요약 생성 + DB 저장
# 마지막 수정일 : 2025-06-12 (수정됨)
def generate_story_plan(state: dict) -> dict:
    theme = state.get("theme")
    mood = state.get("mood")
    topic = state.get("input")  # 사용자 입력 주제
    age = state.get("age", 7)
    story_id = state.get("story_id")  # story_id 반드시 필요

    # 1. 시스템 지침 (system message style)
    system_instruction = (
        f"You are a professional children's story writer for age {age}.\n"
        "Your task is to create a story outline using the classic Korean 4-stage structure: 기 (Introduction), 승 (Development), 전 (Climax), 결 (Conclusion).\n"
        "Use the provided topic, theme, and mood to generate a short and coherent outline.\n"
        "The story should include 1–2 main characters with detailed traits: name, gender, hair color, eye color, age, and species (human, animal, monster, etc).\n"
        "Use character names introduced in the topic or invent natural-sounding Korean names.\n"
        "Do not rely on typical animal stereotypes from fables like 'The Tortoise and the Hare'.\n"
        "The rabbit or turtle can have reversed personalities.\n"
        "Follow the user's paragraph and implied traits instead of assuming standard roles.\n"
        "Do not give human names to animal or non-human characters. "
        "For animal or non-human characters (e.g. rabbits, turtles, goblins), use imaginative or nickname-style Korean names such as 루루, 뭉치, 아롱이, 포코.\n"
        "Do NOT use human names (e.g. 민준, 수아, 보람) for animals or fantasy creatures.\n"
        "Only give human names to human characters."
        "Keep character names consistent across all 4 stages.\n"
        "All output must be in Korean."
    )

    # 2. 사용자 요청 (user prompt style)
    user_request = (
        f"[Input Information]\n"
        f"- Topic: {topic}\n"
        f"- Theme: {theme}\n"
        f"- Mood: {mood}\n\n"
        "[Output Format Example]\n"
        "[기승전결]\n"
        "1. 기: 마을 소녀 수아는 어느 날 숲 속에서 신비한 알을 발견한다.\n"
        "2. 승: 수아는 알을 돌보던 중 알에서 용이 깨어나고, 두려움과 호기심 사이에서 갈등한다.\n"
        "3. 전: 마을 사람들은 용을 해치려 하고, 수아는 용을 구하기 위해 도망친다.\n"
        "4. 결: 수아는 용과 함께 숲 속에서 살아가기로 결심하고 마을을 떠난다.\n\n"
        "[등장인물]\n"
        "1. 수아 : 여자, 노란 머리, 파란 눈동자, 7세, 인간\n"
        "2. 용 : 남성, 검은 머리, 검은 눈동자, 100세, 용\n\n"
        "→ Your output must include both [기승전결] and [등장인물] sections.\n"
        "Each item must begin with a number and period (e.g., '1. ...').\n"
        "Do NOT include any title, markdown, or bullet points.\n"
        "The entire response must be written clearly in Korean.\n"
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': "Understood. I will generate a 4-stage story outline and character list in Korean based on the given theme, mood, and topic."}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    result = response.text.strip()

    # 결과 파싱
    story_plan, characters = [], []
    current_section = None
    for line in result.splitlines():
        if "[기승전결]" in line:
            current_section = "summary"
            continue
        elif "[등장인물]" in line:
            current_section = "characters"
            continue
        if re.match(r"^\d+\.", line.strip()):
            if current_section == "summary":
                story_plan.append(line.strip())
            elif current_section == "characters":
                characters.append(line.strip())

    story = Story.objects.get(story_id=story_id)
    story.summary_4step = "\n".join(story_plan)
    story.characters = "\n".join(characters)
    story.save()

    if debug:
        print("\n" + "-" * 40)
        print("1. [GenerateStoryPlan] DEBUG LOG")
        print("-" * 40)
        print(f"Story ID     : {story_id}")
        print(f"Topic        : {topic}")
        print(f"Theme        : {theme}")
        print(f"Mood         : {mood}")
        print(f"Age          : {age}")
        print("Story Plan   :")
        for s in story_plan:
            print(f"  {s}")
        print("Characters   :")
        for c in characters:
            print(f"  {c}")
        print("-" * 40 + "\n")

    return {
        **state,
        "story_plan": story_plan,
        "characters": characters
    }


# 작성자 : 최준혁
# 기능 : 벡터 DB에서 관련 문맥을 조회하여 상태에 context로 추가
# 마지막 수정일 : 2025-06-10
def retrieve_context(state: dict) -> dict:
    query = state.get("input", "")
    story_id = state.get("story_id")
    paragraph_no = state.get("paragraph_no") 

    # 첫 문단인 경우 context 비움
    if paragraph_no == 1:
        print("[RetrieveContext] 첫 문단이므로 context 비움")
        return {
            **state,
            "context": ""
        }

    retrieved_context = ""

    try:
        # 우선 벡터 검색 시도
        retrieved_context = search_similar_paragraphs(story_id, query, top_k=6)
        if not retrieved_context:
            print("[RetrieveContext] 벡터 검색 결과 없음. 최근 문단 사용.")
            retrieved_context = get_latest_paragraphs(story_id, top_k=6)
    except Exception as e:
        print(f"[RetrieveContext Error] {e}")
        retrieved_context = get_latest_paragraphs(story_id, top_k=6)

    if not retrieved_context:
        retrieved_context = "이전에 생성된 문맥이 없습니다."

    if debug:
        print("\n" + "-"*40)
        print("2. [RetrieveContext] DEBUG LOG")
        print("-"*40)
        print(f"Story ID     : {story_id}")
        print(f"Paragraph No : {paragraph_no}")
        print(f"Retrieved Context:\n{retrieved_context}")
        print("-"*40 + "\n")

    return {
        **state,
        "context": retrieved_context
    }


# 작성자 : 최준혁
# 기능 : 사용자 입력을 받아 동화 패러그래프를 생성하는 노드
# 마지막 수정일 : 2025-06-15
def get_paragraph_hint(paragraph_no: int) -> str:
    if paragraph_no >= 9:
        return (
            "- This is the final part of the story. You MUST wrap things up within the next 1–2 paragraphs.\n"
            "- Do not start new events or characters.\n"
            "- Keep the emotional arc consistent and conclude any remaining threads.\n"
        )
    elif paragraph_no >= 7:
        return (
            "- Only a few paragraphs left before the end. Begin guiding the story toward its conclusion.\n"
            "- Avoid introducing new subplots.\n"
        )
    return ""

def get_force_final_ending_instruction(stage: str, paragraph_no: int) -> str:
    if stage == "결" and paragraph_no == 10:
        return (
            "\n\nFinal Ending Instruction:\n"
            "- This is the final paragraph of the story.\n"
            "- You MUST conclude the story in a clear, satisfying, and emotional way suitable for children.\n"
            "- DO NOT ask a follow-up question or provide any [행동] options.\n"
            "- Just write the final [문장] that wraps up the story completely.\n"
            "- Make sure the child understands this is the ending.\n"
        )
    return ""

def generate_paragraph(state: dict) -> dict:
    user_input = state.get("input")
    user_age = state.get("age")
    theme = state.get("theme")
    mood = state.get("mood")
    context = state.get("context")
    story_plan = state.get("story_plan", [])

    last_para = Storyparagraph.objects.filter(story_id=state.get("story_id")).order_by("-paragraph_no").first()
    paragraph_no = (last_para.paragraph_no + 1) if last_para else 1

    story_stage = get_story_stage(paragraph_no)

    stage_to_index = {"기": 0, "승": 1, "전": 2, "결": 3}
    plan_summary = story_plan[stage_to_index[story_stage]] if len(story_plan) > stage_to_index[story_stage] else ""

    paragraph_hint = get_paragraph_hint(paragraph_no)
    force_final_ending_instruction = get_force_final_ending_instruction(story_stage, paragraph_no)

    system_instruction = (
        "You are a professional Korean children's story writer.\n"
        "Your tone should be warm, gentle, and immersive, like reading a picture book to a child.\n"
        "Use simple, age-appropriate language for a child aged "
        f"{user_age}.\n"
        "- NEVER use emojis, markdown, or sound effects (e.g., '아!', '얘야').\n"
        "- DO NOT repeat the stage summary or previously told story.\n"
        "- DO NOT give human names to animal or fantasy characters (use names like 루루, 뭉치, 포코).\n"
        "- Do NOT assign the same name to more than one character, even if they are different species.\n"
        "- Each character must have a unique name.\n"
        "- Maintain a consistent naming convention throughout the story.\n"
        "- Encourage the child to imagine or choose the next step using the provided [질문] and [행동] sections.\n"
    )

    user_request = (
        f"Child's New Input:\n"
        f"\"{user_input}\"\n\n"
        "→ This is a NEW event or suggestion from the child.\n"
        "→ You MUST reflect this in the story continuation.\n"
        "→ Treat this input as the most recent plot development after the story so far.\n"
        "→ DO NOT ignore or skip this input.\n\n"

        "Stage Summary (from Story Plan):\n"
        f"{plan_summary if plan_summary else '요약 없음'}\n\n"

        "Current Context:\n"
        f"{context}\n\n"

        f"Theme: {theme}\n"
        f"Mood: {mood}\n"
        f"Child Age: {user_age}세\n"
        f"Story Stage: '{story_stage}'\n"
        f"{paragraph_hint}"
        f"{force_final_ending_instruction}\n\n"

        "Instructions:\n"
        "Use the following format:\n"
        "[문장] - Continue the story in 3–6 Korean sentences.\n"
        "[질문] - Ask ONE child-directed question in Korean about what should happen next.\n"
        "[행동] - List 3 clear action choices the child can select. Each must be a full sentence.\n\n"

        "Formatting Constraints:\n"
        "- Each choice in [행동] must end with ~해요 / ~어요 / ~한다.\n"
        "- DO NOT phrase choices as questions or suggestions (e.g., '~할까요?', '~볼래요?').\n"
        "- Choices must describe what the character does, not what the child should do.\n"
        "- NEVER use emojis, markdown, or sound effects.\n"
        "- DO NOT repeat the story summary or previous context.\n\n"

        "Character Naming Rules:\n"
        "- Animal or fantasy characters (e.g., talking dogs, fairies, goblins) must NEVER have human names.\n"
        "- Only human characters may have Korean names like 민준 or 수아.\n"
        "- Each character must have a unique name across the entire story.\n\n"

        "Stage-Specific Guidance:\n"
        "- '기' (Beginning):\n"
        "   * Introduce the main character with name, age, and personality.\n"
        "   * Show their NORMAL daily life (e.g., habits, routines).\n"
        "   * Set the scene (place, time, atmosphere).\n"
        "   * Introduce ONE mysterious or magical element, and ONLY in the final sentence.\n"
        "   * If a new character appears, clearly state what kind of being it is (e.g., a goose, a pony, a human).\n"

        "- '승' (Development):\n"
        "   * You MAY introduce a new helper or problem character if it naturally fits the conflict.\n"
        "   * Avoid unnecessary characters; use existing ones if possible.\n"
        "   * Describe their appearance and motivation.\n"
        "   * Begin building a challenge or conflict.\n"

        "- '전' (Climax):\n"
        "   * DO NOT introduce new characters or settings.\n"
        "   * Present the peak moment of tension.\n"
        "   * Focus on the character's inner struggle or important decision.\n"

        "- '결' (Conclusion):\n"
        "   * DO NOT add surprises or new elements.\n"
        "   * Help the child feel resolution and peace.\n"
        "   * Use soft emotional reflection and lead gently to the ending.\n\n"

        "Important:\n"
        "- You MUST always include [문장], [질문], and [행동].\n"
        "- EXCEPTION: If this is the 10th paragraph and the stage is '결', then ONLY write [문장] (the complete ending).\n"
        "- The [행동] MUST reflect the current story stage and help transition to the next natural stage in the 4-step plan.\n"
        "- DO NOT introduce irrelevant or disconnected directions.\n"
        "- DO NOT derail the story with illogical or abrupt shifts.\n"
        "- Choices must align with the planned story arc (기-승-전-결).\n"
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': '네, 알겠습니다. 전문적인 한국 동화 작가로서 아이의 나이에 맞춰 따뜻한 말투로 이야기를 만들겠습니다. 요청하신 형식에 맞춰 답변해 드릴게요.'}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    full_text = response.text.strip()

    paragraph, question, choices = extract_choice(full_text)

    if debug:
        print("\n" + "="*40)
        print("3. [GenerateParagraph] DEBUG LOG")
        print("="*40)
        print(f"문단 번호: {paragraph_no} / 이야기 단계: {story_stage}")
        print(f"현재 요약: {plan_summary}")
        print(f"생성된 문단:\n{paragraph}")
        print(f"질문: {question}")
        print(f"선택지: {choices}")
        print("="*40 + "\n")

    return {
        "input": user_input,
        "paragraph_text": paragraph,
        "question": question,
        "choices": choices,
        "mood": mood,
        "context": context,
        "paragraph_no": paragraph_no
    }



# ------------------------------------------------------------------------
# 페러그래프 수정 관련
# ------------------------------------------------------------------------

# # 작성자 : 최준혁
# # 기능 : 이름에 대한 중복 여부 체크
# # 마지막 수정일 : 2025-06-12
def is_similar_name(name: str, known_names: list[str], threshold: float = 0.8) -> bool:
    name_norm = normalize_name(name)
    for kn in known_names:
        ratio = difflib.SequenceMatcher(None, name_norm, normalize_name(kn)).ratio()
        if debug:
            print(f"[SimilarityCheck] {name_norm} vs {kn} → {ratio:.2f}")
        if ratio >= threshold:
            return True
    return False

# 작성자 : 최준혁
# 기능 : 이름과 전체 프로필 유사도를 함께 고려해 중복 인물 여부 판단
# 마지막 수정일 : 2025-06-15
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


# 작성자 : 최준혁
# 기능 : 이름에 대한 유사도 측정
# 마지막 수정일 : 2025-06-15
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


# 작성자 : 최준혁
# 기능 : 문단에서 등장하는 인물들 중 '스토리 전개에 의미 있는 영향을 준 인물'만 골라서 이름만 리스트로 출력하는 함수
# 마지막 수정일 : 2025-06-15
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



# 작성자 : 최준혁
# 기능 : 문단에서 새롭게 등장한 인물 이름을 추출하는 함수
# 마지막 수정일 : 2025-06-12
def extract_new_characters(text: str, known_names: list[str]) -> list[str]:
    system_instruction = (
        "You are a smart assistant helping identify characters in a Korean children's story.\n"
        "Your task is to extract ONLY the proper names of characters who actively appear, speak, or perform actions in the paragraph.\n"
        "Exclude any beings or terms that only refer to abstract concepts, metaphors, locations, or symbolic entities (like 어비스, 꿈, 세계, 별 등).\n"
        "Only include character names who are PERSONIFIED and visibly present in the scene.\n"
        "**Do NOT include meaningless interjections or animal sounds (e.g., “neigh”, “woof”, “meow”) as character names.**\n"
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



# 작성자 : 최준혁
# 기능 : 사용자의 입력으로 새롭게 추가되는 등장인물의 특징을 추정하는 함수
# 마지막 수정일 : 2025-06-13
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
        f"→ Avoid vague labels like “unknown” or “none” — always infer a likely gender, age, and species based on the context.\n"
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


# 작성자 : 최준혁
# 기능 : 사용자 입력을 통해 Story 테이블의 characters와 summary_4step을 수정하는 메인 함수
# 마지막 수정일 : 2025-06-15 (리팩토링: 현재 문단 등장 인물 기반, 고정 인물 강제 포함)
def detect_and_update_story(state: dict) -> dict:
    if state.get("paragraph_no", 1) == 1:
        print("[DetectUpdate] 첫 문단이므로 스킵")
        return state

    story_id = state.get("story_id")
    paragraph_text = state.get("paragraph_text", "")
    user_input = state.get("input", "")
    age = state.get("age", 7)
    mood = state.get("mood", "")
    theme = state.get("theme", "")
    paragraph_no = state.get("paragraph_no", 1)

    story = Story.objects.filter(story_id=story_id).first()
    if not story:
        print(f"[DetectUpdate] story_id {story_id} not found.")
        return state

    if is_choice_only(user_input):
        print("[DetectUpdate] 선택지 입력만 포함된 것으로 판단 → 캐릭터 및 요약 업데이트 스킵")
        return {**state, "characters": story.characters.splitlines() if story.characters else []}

    prev_character_lines = story.characters.splitlines() if story.characters else []
    prev_char_map = {
        re.split(r"[:：]", line)[0].split(".", 1)[-1].strip(): line
        for line in prev_character_lines
    }

    protagonist_name = None
    if prev_char_map:
        protagonist_name = list(prev_char_map.keys())[0]

    raw_names = extract_new_characters(paragraph_text + "\n" + user_input, list(prev_char_map.keys()))
    current_names = filter_significant_characters(paragraph_text, raw_names, user_input)

    if not current_names:
        if debug:
            print("[DetectUpdate] No valid new characters found.")
        return {**state, "characters": list(prev_char_map.values())}

    if debug:
        print(f"[DetectUpdate] New characters detected: {current_names}")

    # 기존 인물은 유지, 새로운 인물만 누적 추가
    new_entries = []

    for name in current_names:
        if name in prev_char_map:
            continue  # 이미 존재하는 인물은 건너뜀 (갱신 금지)
        else:
            desc = get_character_description(name, paragraph_text, user_input, age, list(prev_char_map.values()))
            if desc and not is_duplicate_character(name, desc, list(prev_char_map.values())):
                prev_char_map[name] = desc
                new_entries.append(desc)
            else:
                if debug:
                    print(f"[중복 제거됨] '{name}'은 유사한 기존 캐릭터로 간주되어 추가되지 않음.")

    # 최종 캐릭터 리스트는 기존 + 신규 (순서 유지)
    all_character_lines = prev_character_lines + new_entries

    # 번호 다시 매기기
    renumbered_characters = []
    seen_names = set()
    for line in all_character_lines:
        name = re.split(r"[:：]", line)[0].split(".", 1)[-1].strip()
        if name not in seen_names:
            seen_names.add(name)
            cleaned = re.sub(r"^\d+\.\s*", "", line)
            renumbered_characters.append(f"{len(renumbered_characters)+1}. {cleaned}")

    story.characters = "\n".join(renumbered_characters)

    new_summary = None
    if paragraph_no < 9 and story.summary_4step:
        existing_lines = story.summary_4step.strip().splitlines()

        system_instruction = (
            f"You are a professional children's story writer for age {age}.\n"
            "Your task is to revise the existing 4-step story summary based on a new character input.\n"
            "Preserve the structure and flow. Reflect meaningful characters only. Do NOT invent."
            "**The output MUST be written in Korean only. DO NOT use English.**"
        )

        user_request = (
            f"[Existing Summary]\n" + "\n".join(existing_lines) + "\n\n"
            f"[Mood]: {mood}\n"
            f"[Theme]: {theme}\n"
            f"[User Input]: {user_input}\n"
            f"[Visible Characters]: {', '.join(current_names)}\n\n"
            "Output 4 numbered lines only."
            "**Write in Korean only. Do NOT use English.**"
        )

        contents = [
            {'role': 'user', 'parts': [{'text': system_instruction}]},
            {'role': 'model', 'parts': [{'text': "Understood."}]},
            {'role': 'user', 'parts': [{'text': user_request}]}
        ]

        response = model.generate_content(contents)
        raw = [line.strip() for line in response.text.strip().splitlines() if re.match(r"^\d+\.\s", line)]
        if len(raw) >= 4:
            new_summary = raw[:4]
            story.summary_4step = "\n".join(new_summary)

    story.save()

    if debug:
        print("\n" + "-" * 40)
        print("4. [DetectUpdate] DEBUG LOG")
        print("-" * 40)
        print(f"Story ID     : {story_id}")
        print(f"User Input   : {user_input}")
        print(f"Characters   :")
        for c in renumbered_characters:
            print(f"  {c}")
        if new_summary:
            print("Updated Summary:")
            for s in new_summary:
                print(f"  {s}")
        print("-" * 40 + "\n")

    new_state = {**state, "characters": renumbered_characters}
    if new_summary and new_summary != "\n".join(state.get("story_plan", [])):
        new_state["story_plan"] = new_summary

    return new_state




# 작성자 : 최준혁
# 기능 : 기존 paragraph_id의 문단 내용을 수정하여 ParagraphVersion에 새 버전을 추가하고,
#        StoryParagraph의 본문도 최신 내용으로 업데이트
# 마지막 수정일 : 2025-06-03
def update_paragraph_version(state: dict) -> dict:
    paragraph_id = state.get("paragraph_id")
    new_text = state.get("paragraph_text")
    user_id = state.get("user_id")

    # 현재 버전 번호 조회
    last_version = Paragraphversion.objects.filter(paragraph_id=paragraph_id).order_by('-version_no').first()
    next_version = (last_version.version_no + 1) if last_version else 2

    # ParagraphVersion 테이블에 새 버전 추가
    Paragraphversion.objects.create(
        paragraph_id=paragraph_id,
        version_no=next_version,
        content_text=new_text,
        generated_by=str(user_id),
        created_at=timezone.now()
    )

    # StoryParagraph 테이블 본문 업데이트
    Storyparagraph.objects.filter(paragraph_id=paragraph_id).update(
        content_text=new_text,
        updated_at=timezone.now()
    )

    if debug:
        print("\n" + "-"*40)
        print("4-1. [UpdateParagraphVersion] DEBUG LOG")
        print("-"*40)
        print(f"Paragraph ID : {paragraph_id}")
        print(f"New Version  : v{next_version}")
        print(f"Updated Text :\n{new_text}")
        print("-"*40 + "\n")

    return {
        "paragraph_id": paragraph_id,
        "paragraph_text": new_text,
        "version_no": next_version
    }


# ------------------------------------------------------------------------
# 페러그래프 저장 관련
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 생성된 패러그래프를 StroyParagraph 테이블에 저장
#       동일한 내용을 ParagraphVersion 테이블에 v1로 저장
# 마지막 수정일 : 2025-06-03
def save_paragraph(state: dict) -> dict:
    story_id = state.get("story_id")
    paragraph_text = state.get("paragraph_text")
    paragraph_no = state.get("paragraph_no")

    if debug:
        print("\n" + "-"*40)
        print("4. [SaveParagraph] DEBUG LOG")
        print("-"*40)
        print(f"Story ID     : {story_id}")
        print(f"Paragraph No : {paragraph_no}")
        print(f"Paragraph Text:\n{paragraph_text}")
        print("-"*40 + "\n")
        
    # StoryParagraph 테이블에 저장
    paragraph = Storyparagraph.objects.create(
        story_id = story_id,
        # paragraph_no = next_no,
        paragraph_no = paragraph_no,
        content_text = paragraph_text,
        created_at = timezone.now(),
        updated_at = timezone.now()
    )

    # ParagraphVersion 저장(v1)
    Paragraphversion.objects.create(
        paragraph_id = paragraph.paragraph_id,
        version_no = 1,
        content_text = paragraph_text,
        generated_by = str(state.get("user_id")),
        created_at = timezone.now()
    )
    
    try:
        index_paragraphs_to_faiss(story_id, [paragraph_text])
    except Exception as e:
        print(f"[VectorStore] 벡터 저장 실패: {e}")

    return {
        **state,
        "paragraph_id": paragraph.paragraph_id,
        "paragraph_no": paragraph_no,
    }

# 작성자 : 최준혁
# 기능 : 사용자 입력과 패러그래프를 ParagraphQA에 저장
# 마지막 수정일 : 2025-06-03
def save_qa(state: dict) -> dict:
    Paragraphqa.objects.create(
        paragraph_id = state.get("paragraph_id"),
        story_id = state.get("story_id"),
        question_text = state.get("input"),
        answer_text = state.get("paragraph_text"),
        created_at = timezone.now()
    )

    if debug:
        print("\n" + "-"*40)
        print("5. [SaveQA] DEBUG LOG")
        print("-"*40)
        print(f"Paragraph ID : {state['paragraph_id']}")
        print(f"Question     : {state['input']}")
        print(f"Answer Text  :\n{state['paragraph_text']}")
        print("-"*40 + "\n")

    return {
        "paragraph_id": state["paragraph_id"],
        "paragraph_text": state["paragraph_text"],
        "input": state["input"]
    }


# ------------------------------------------------------------------------------------------
# 문자열 파싱 함수 
# ------------------------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : Gemini의 응답을 파싱하여 문장, 질문, 선택지로 분리
# 마지막 수정일 : 2025-06-10
def extract_choice(text: str):
    # 예: [문장], [질문], [행동] 기준으로 나누기
    match = re.search(r"\[문장\](.*?)\[질문\](.*?)\[행동\](.*)", text, re.DOTALL)
    if not match:
        return text.strip(), "", []  # 실패 시 전체 반환
    
    paragraph = match.group(1).strip()
    question = match.group(2).strip()
    actions_raw = match.group(3).strip()
    # 줄바꿈으로 나눠서 리스트화
    choices = [line.strip("-•*●· ") for line in actions_raw.split("\n") if line.strip()]
    return paragraph, question, choices



# 작성자 : 최준혁
# 기능 : 이야기 종료를 위해 paragraph_no가 10이상이면 False, 아니면 True 반환
# 마지막 수정일 : 2025-06-11
def check_continue_or_end(state: "StoryState") -> dict:
    if state.get("paragraph_no", 1) >= 10:
        return {**state, "continue_story": False}
    return {**state, "continue_story": True}


# 작성자 : 최준혁
# 기능 : 기승전결 분할
# 마지막 수정일 : 2025-06-12
def get_story_stage(paragraph_no: int) -> str:
    if paragraph_no <= 2:
        return "기"
    elif paragraph_no <= 5:
        return "승"
    elif paragraph_no <= 8:
        return "전"
    else:
        return "결"

# 작성자 : 최준혁
# 기능 : extract_new_characters에서 사용하는 이름 정규화 함수
# 마지막 수정일 : 2025-06-14
def normalize_name(name: str) -> str:
    name = re.sub(r"(님|씨|양|군|아저씨|형|누나|오빠|이모|삼촌|선생님)$", "", name)
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', name).lower()



# 작성자 : 최준혁
# 기능 : 사용자 입력이 선택지만 포함되어 있는지 확인하는 함수
# 마지막 수정일 : 2025-06-15
def is_choice_only(text: str) -> bool:
    lines = [line.strip() for line in text.strip().splitlines()]
    return all(re.match(r"^\d+\.\s", line) for line in lines if line)


# 작성자 : 최준혁
# 기능 : 등장인물 리스트에서 번호를 1부터 다시 매김
# 마지막 수정일 : 2025-06-15
def renumber_characters(character_lines: list[str]) -> list[str]:
    result = []
    for idx, line in enumerate(character_lines, 1):
        # 기존 번호 제거 ("1. 라이카 : ..." → "라이카 : ...")
        line_clean = re.sub(r"^\d+\.\s*", "", line).strip()
        result.append(f"{idx}. {line_clean}")
    return result
# ------------------------------------------------------------------------------------------
# 이미지 생성 관련
# ------------------------------------------------------------------------------------------

THEME_MOOD_LABELS = {
    ("로맨스", "잔잔한"): ["연인", "노을", "공원"],
    ("로맨스", "슬픈"): ["눈물", "편지", "비"],
    ("판타지", "신비로운"): ["마법", "용", "성"],
    ("SF", "긴장감"): ["우주선", "전투", "외계인"],
    ("미스터리", "긴장감"): ["탐정", "그림자", "단서"],
    ("고전", "따뜻한"): ["성", "옛날 옷", "마차"],
    # 기타 등등 추가
}

# 작성자 : 최준혁
# 기능 : 생성된 패러그래프에 따라 이미지 생성 여부를 판단
# 마지막 수정일 : 2025-06-08
def image_prompt_check(state: dict) -> dict:
    paragraph = state.get("paragraph_text", "")

    prompt = (
        # 프롬프트를 강화하거나, 프론트에서 이미지 태그 트리거를(버튼?) 주거나
        "다음 문단은 동화의 일부입니다. 이 문단이 시작적인 이미지로 표현하기에 적합하다면  'yes', "
        "그렇지 않다면 'no'만 출력해주세요. 다른 설명은 필요하지 않습니다. \n\n"
        f"문단 : {paragraph}"
    )

    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        generate_image = "yes" in output
        if debug:
            print(f"[ImagePromptCheck] output: {output}")
    except Exception as e:
        print(f"[ImagePromptCheck Error] {e}")
        generate_image = False

    return {
        **state,
        "image_required": generate_image
    }


# 작성자 : 최준혁
# 기능 : 이미지 생성 더미 노드
# 마지막 수정일 : 2025-06-08
def generate_image(state: dict) -> dict:
    theme = state.get("theme", "판타지 (SF/이세계)")
    mood = state.get("mood", "신비로운")
    image_url = state.get("image_url", "")
    caption_text = state.get("caption", "")

    labels = find_labels_by_theme_and_mood(theme, mood)

    # 디버깅용
    if debug:
        print(f"5. [GenerateImage] 이미지 URL: {image_url}, caption: {caption_text}")
        print(f"[GenerateParagraph] theme: {theme}, mood: {mood}")



    return {
        "image_url": f"https://dummyimage.com/600x400/000/fff&text=Image",
        "caption": f"{theme} 테마의 {mood} 분위기를 담은 이미지",
        "labels": labels
    }
    


# 작성자 : 최준혁
# 기능 : 테마와 분위기에 따른 이미지 라벨을 찾는 함수
# 마지막 수정일 : 2025-06-08
def find_labels_by_theme_and_mood(theme: str, mood: str) -> list:
    for (key_theme, key_mood), labels in THEME_MOOD_LABELS.items():
        if key_theme == theme and key_mood == mood:
            return labels
    return ["기본", "이미지", "라벨"]


# --------------------------------------------------------------------------
# 동화 요약 및 마무리
# --------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 동화의 제목을 짓고, 요약 및 전체 문단을 자연스럽게 연결한 완결형 이야기 본문을 생성
# 마지막 수정일 : 2025-06-15
def finalize_story_output(state: dict) -> dict:
    from api.models import Story, Storyparagraph
    from django.utils import timezone

    story_id = state.get("story_id")
    if not story_id:
        print("[FinalizeStory] story_id 없음")
        return state

    # 1. 전체 문단 취합
    paragraphs = (
        Storyparagraph.objects
        .filter(story_id=story_id)
        .order_by("paragraph_no")
        .values_list("content_text", flat=True)
    )
    full_text = "\n".join(paragraphs)

    # 2. Gemini 프롬프트
    prompt = (
        "다음은 하나의 동화 전체 문단입니다.\n"
        "이 동화를 바탕으로 아래 세 가지를 순서대로 작성해 주세요:\n"
        "1. 감성적인 제목 (15자 이내)\n"
        "2. 3문장 이내의 요약\n"
        "3. 전체 문단을 자연스럽게 연결한 완결형 이야기 본문\n\n"
        "출력 형식:\n"
        "1. 제목: ...\n"
        "2. 요약: ...\n"
        "3. 본문: ...\n\n"
        "한국어로 작성해 주세요.\n\n"
        f"{full_text}"
    )

    response = model.generate_content(prompt)
    lines = response.text.strip().splitlines()

    # 3. 파싱 로직 (레이블 유연 대응)
    def extract_section(prefixes: list[str]) -> str:
        for line in lines:
            for p in prefixes:
                if line.strip().startswith(p):
                    return line.split(":", 1)[-1].strip()
        return ""

    title = extract_section(["1.", "1. 제목", "1. 목", "제목", "목"])
    summary = extract_section(["2.", "2. 요약", "2. 약", "요약", "약"])

    narrative_lines = []
    capture = False
    for line in lines:
        if any(line.strip().startswith(p) for p in ["3.", "3. 본문", "3. 문", "본문", "문"]):
            capture = True
            narrative_lines.append(line.split(":", 1)[-1].strip())
            continue
        if capture:
            narrative_lines.append(line.strip())
    full_narrative = "\n".join([l for l in narrative_lines if l])

    # 4. Story에 저장
    story = Story.objects.filter(story_id=story_id).first()
    if story:
        story.title = title
        story.summary = summary
        story.status = "completed"
        story.save()

    # 5. 문단 나눠서 Storyparagraph에 추가 저장
    existing_para = (
        Storyparagraph.objects
        .filter(story_id=story_id)
        .order_by("-paragraph_no")
        .first()
    )
    last_para_no = existing_para.paragraph_no if existing_para else 0
    split_paragraphs = [p.strip() for p in full_narrative.split("\n") if p.strip()]
    next_para_no = last_para_no + 1

    for i, para in enumerate(split_paragraphs):
        Storyparagraph.objects.create(
            story_id=story.story_id,
            paragraph_no=next_para_no + i,
            content_text=para,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

    print("\n" + "-" * 40)
    print("[FinalizeStory] 저장 완료")
    print(f"제목       : {title}")
    print(f"단락 개수  : {len(split_paragraphs)}")
    print("-" * 40 + "\n")

    return {
        **state,
        "title": title,
        "summary_3line": summary,
        "narrative_story": full_narrative
    }
