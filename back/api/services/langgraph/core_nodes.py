# LangGraph 핵심 생성 노드 정의
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15
import google.generativeai as genai
import os
import re
from typing import Tuple, List

from api.models import Story, Storyparagraph
from django.utils import timezone
from api.services.vector_utils import search_similar_paragraphs, get_latest_paragraphs
from .parsing_utils import extract_choice
from .summary_utils import get_story_stage

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 초기화 및 모델 정의
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------------------------------------------------------------------
# 기승전결 생성
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 주제/분위기 기반 4단계 요약 생성 + DB 저장
# 마지막 수정일: 2025-06-12
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


# ------------------------------------------------------------------------------------------
# 문맥 조회
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 벡터 DB에서 관련 문맥을 조회하여 상태에 context로 추가
# 마지막 수정일: 2025-06-10
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

# 작성자: 최준혁
# 기능: 문단 번호에 따른 힌트 제공
# 마지막 수정일: 2025-06-11
def get_paragraph_hint(paragraph_no: int) -> str:
    """문단 번호에 따른 힌트 제공"""
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

# 작성자: 최준혁
# 기능: 마지막 문단 강제 종료 지침
# 마지막 수정일: 2025-06-15
def get_force_final_ending_instruction(stage: str, paragraph_no: int) -> str:
    if stage == "결" and paragraph_no == 10:
        return (
            "\n\nFinal Ending Instruction:\n"
            "- This is the final paragraph of the story.\n"
            "- You MUST conclude the story in a warm, clear, and emotionally satisfying way suitable for children.\n"
            "- The ending must feel complete. Do NOT imply that the story continues.\n"
            "- Do NOT include any follow-up questions or action choices.\n"
            "- You MUST include a clear final sentence that signals the story has ended (e.g., 'From that day on...', 'Since then...', 'And the adventure came to an end.').\n"
            "- Just write the [문장] that clearly wraps up the story.\n"
            "- Examples:\n"
            "  • 'And from that day on, Minjun lived peacefully with his magical friends.'\n"
            "  • 'Minjun smiled, knowing he had found courage inside himself.'\n"
            "  • 'The forest was quiet again, and the stars twinkled gently above.'\n"
        )
    return ""



# ------------------------------------------------------------------------------------------
# 문단 생성
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 사용자 입력을 받아 동화 패러그래프를 생성하는 노드
# 마지막 수정일: 2025-06-15
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
