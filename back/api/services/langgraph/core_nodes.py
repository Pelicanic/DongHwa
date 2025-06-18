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
from api.services.relational_utils import search_similar_paragraphs_by_keywords, get_latest_paragraphs
from .parsing_utils import extract_choice
from .substage_prompts import get_substage_instruction  

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 초기화 및 모델 정의
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------------------------------------------------------------------
# 1. 기승전결 생성
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 주제/분위기 기반 10단계 요약 생성 + DB 저장
# 마지막 수정일: 2025-06-17
def generate_story_plan(state: dict) -> dict:
    theme = state.get("theme")
    mood = state.get("mood")
    topic = state.get("input")  # 사용자 입력 주제
    age = state.get("age", 7)
    story_id = state.get("story_id")  # story_id 반드시 필요

    # 1. 시스템 지침 
    system_instruction = (
        f"You are a professional children's story writer for age {age}.\n"
        "Your task is to create a story outline using a 10-step version of the classic Korean 4-stage structure: 기 (Introduction), 승 (Development), 전 (Climax), 결 (Conclusion).\n"
        "Use the provided topic, theme, and mood to generate a coherent, emotionally progressive 10-sentence outline.\n"
        "Each sentence should represent a key transition in the story's development.\n"
        "Keep characters, setting, and tone consistent. Do NOT change place/time or introduce new characters after step 5.\n"
        "Use only 1–2 main characters with clear details: name, gender, age, species, hair, eyes.\n"
        "Use nickname-style Korean names for animals or fantasy characters.\n"
        "Write clearly in Korean. No markdown or explanations."
    )

    # 2. 사용자 요청 
    user_request = (
        f"[Input Information]\n"
        f"- Topic: {topic}\n"
        f"- Theme: {theme}\n"
        f"- Mood: {mood}\n\n"

        "[Output Format Example]\n"
        "[기승전결]\n"
        "1. 기1: 주인공이 평소 어떤 삶을 살고 있는지 소개한다.\n"
        "2. 기2: 조용한 일상 속에서 작은 이상 징후가 감지된다.\n"
        "3. 승1: 그 이상 현상이 점점 커지며 문제의 조짐을 보인다.\n"
        "4. 승2: 주인공이 사태에 반응하고, 감정 변화가 시작된다.\n"
        "5. 승3: 문제 상황이 점점 더 복잡해지고, 갈등이 확대된다.\n"
        "6. 전1: 가장 큰 위기 상황이 벌어지며 절정에 이른다.\n"
        "7. 전2: 주인공이 중요한 결단을 내리거나 변화한다.\n"
        "8. 결1: 문제 해결을 위한 행동이 시작된다.\n"
        "9. 결2: 사건이 마무리되고 감정적으로 정리된다.\n"
        "10. 에필로그: 평화로운 결말과 함께 교훈이나 여운을 남긴다.\n\n"
        
        "[등장인물]\n"
        "1. 수아 : 여자, 노란 머리, 파란 눈동자, 7세, 인간\n"
        "2. 용이 : 남성, 검은 머리, 검은 눈동자, 100세, 용\n\n"
        "→ 반드시 1~10 단계 문장과 [등장인물] 섹션을 포함해야 합니다.\n"
        "→ 각 문장은 '1. ~', '2. ~' 형식으로 시작하세요."
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {'role': 'model', 'parts': [{'text': "Understood. I will generate a 10-stage story outline and character list in Korean."}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    result = response.text.strip()

    # 결과 파싱
    story_plan, characters = [], []
    current_section = "summary"
    for line in result.splitlines():
        if "[등장인물]" in line:
            current_section = "characters"
            continue
        if re.match(r"^\d+\. ", line.strip()):
            if current_section == "summary":
                story_plan.append(line.strip())
            elif current_section == "characters":
                characters.append(line.strip())

    # DB 저장 - 캐시된 Story 객체 사용
    story = state.get("story")
    if not story:
        # 캐시가 없으면 직접 조회
        story = Story.objects.get(story_id=story_id)

    story.summary_4step = "\n".join(story_plan)
    story.characters = "\n".join(characters)
    story.save()

    if debug:
        print("\n" + "-" * 40)
        print("1. [GenerateStoryPlan] DEBUG LOG (10단계 기승전결)")
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
# 2. 문맥 조회
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 관계형 DB에서 관련 문맥을 조회하여 상태에 context로 추가 (벡터DB 대체)
# 마지막 수정일: 2025-06-16
def retrieve_context(state: dict) -> dict:
    query = state.get("input", "")
    story_id = state.get("story_id")
    paragraph_no = state.get("paragraph_no") 

    # 11번째 문단 이상 요청 시 거부
    if not paragraph_no:  # paragraph_no가 설정되지 않은 경우 계산
        last_para = Storyparagraph.objects.filter(story_id=story_id).order_by("-paragraph_no").first()
        paragraph_no = (last_para.paragraph_no + 1) if last_para else 1
    
    if paragraph_no >= 11:
        if debug:
            print(f"[RetrieveContext] 11번째 문단 요청 거부 - paragraph_no: {paragraph_no}")
        return {
            **state,
            "context": "동화가 이미 완성되었습니다.",
            "paragraph_no": paragraph_no,
            "story_completed": True
        }

    # 첫 문단인 경우 context 비움
    if paragraph_no == 1:
        if debug:
            print("[RetrieveContext] 첫 문단이므로 context 비움")
        return {
            **state,
            "context": ""
        }

    retrieved_context = ""

    try:
        # 관계형 DB에서 키워드 기반 검색 시도 (벡터DB 대체)
        retrieved_context = search_similar_paragraphs_by_keywords(story_id, query, top_k=6)
        if not retrieved_context:
            if debug:
                print("[RetrieveContext] 키워드 검색 결과 없음. 최근 문단 사용.")
            retrieved_context = get_latest_paragraphs(story_id, top_k=6)
    except Exception as e:
        if debug:
            print(f"[RetrieveContext Error] {e}")
        retrieved_context = get_latest_paragraphs(story_id, top_k=6)

    if not retrieved_context:
        retrieved_context = "이전에 생성된 문맥이 없습니다."

    if debug:
        print("\n" + "-"*40)
        print("2. [RetrieveContext] DEBUG LOG (관계형 DB)")
        print("-"*40)
        print(f"Story ID     : {story_id}")
        print(f"Paragraph No : {paragraph_no}")
        print(f"Query        : {query}")
        print(f"Context 길이  : {len(retrieved_context)}자")
        if retrieved_context != "이전에 생성된 문맥이 없습니다.":
            print(f"Context 미리보기:\n{retrieved_context[:200]}...")
        print("-"*40 + "\n")

    return {
        **state,
        "context": retrieved_context
    }

# ------------------------------------------------------------------------------------------
# 3. 문단 생성
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 문단 번호에 따른 이야기 단계 반환
# 마지막 수정일: 2025-06-16
def get_story_substage(paragraph_no: int) -> str:
    if paragraph_no == 1:
        return "기1"
    elif paragraph_no == 2:
        return "기2"
    elif paragraph_no == 3:
        return "승1"
    elif paragraph_no == 4:
        return "승2"
    elif paragraph_no == 5:
        return "승3"
    elif paragraph_no == 6:
        return "전1"
    elif paragraph_no == 7:
        return "전2"
    elif paragraph_no == 8:
        return "결1"
    elif paragraph_no == 9:
        return "결2"
    elif paragraph_no == 10:
        return "에필로그"
    else:
        return "에필로그"  # 10 초과일 경우에도 에필로그로 간주


# 작성자: 최준혁
# 기능: 문단 번호에 따른 힌트 제공
# 마지막 수정일: 2025-06-11
def get_paragraph_hint(substage: str) -> str:
    if substage == "기1":
        return (
            "- This is the beginning. Introduce the main character and their peaceful routine.\n"
        )
    elif substage == "기2":
        return (
            "- A small oddity appears. Let curiosity emerge, but stay gentle."
        )
    elif substage == "승1":
        return (
            "- First clear tension. Start shifting from peace to conflict."
        )
    elif substage == "승2":
        return (
            "- The character begins to engage with the problem. Show their response."
            "- It’s okay to introduce a helper if needed.\n"
        )
    elif substage == "승3":
        return (
            "- Tension rises. Reveal internal or external challenges."
        )
    elif substage == "전1":
        return (
            "- The crisis peaks. Everything should feel urgent, risky, or highly emotional.\n"
            "- No new characters or places.\n"
        )
    elif substage == "전2":
        return (
            "- Turning point. The character makes a key decision."
        )
    elif substage == "결1":
        return (
            "- Begin resolving the conflict. Emotional tone should soften.\n"
            "- Guide toward a peaceful resolution.\n"
        )
    elif substage == "결2":
        return (
            "- Final emotional closure. Highlight reflections or lessons learned.\n"
            "- Prepare for the story’s end.\n"
        )
    elif substage == "에필로그":
        return (
            "- Write a complete 3-6 sentence [문장] that beautifully closes the story.\n"
            "- No [질문] or [행동]. Use peaceful, conclusive tone.\n"
            "- Provide proper emotional closure and story resolution.\n"
        )
    return ""


# 작성자: 최준혁
# 기능: 마지막 문단 강제 종료 지침
# 마지막 수정일: 2025-06-15
def get_force_final_ending_instruction(stage: str, paragraph_no: int) -> str:
    if stage == "에필로그" and paragraph_no == 10:
        return (
            "\n\nFinal Ending Instruction:\n"
            "- This is the final paragraph of the story.\n"
            "- You MUST end the story.\n"
            "- Write 3-6 engaging sentences in the [문장] section to properly conclude the story.\n"
            "- You MUST conclude the story in a warm, clear, and emotionally satisfying way suitable for children.\n"
            "- DO NOT include any [질문] or [행동] sections.\n"
            "- The ending must feel complete. Do NOT imply that the story continues.\n"
            "- Finish with a clear emotional conclusion.\n"
            "- You MUST include a clear final sentence that signals the story has ended (e.g., 'From that day on...', 'Since then...', 'And the adventure came to an end.').\n"
            "- Write the full [문장] section with sufficient detail, not just a brief summary.\n"
        )
    return ""


# 작성자: 최준혁
# 기능: 사용자 입력을 받아 동화 패러그래프를 생성하는 노드
# 마지막 수정일: 2025-06-17
def generate_paragraph(state: dict) -> dict:
    user_input = state.get("input")
    user_age = state.get("age")
    theme = state.get("theme")
    mood = state.get("mood")
    context = state.get("context")
    story_plan = state.get("story_plan", [])
    story_id = state.get("story_id")

    last_para = Storyparagraph.objects.filter(story_id=story_id).order_by("-paragraph_no").first()
    paragraph_no = (last_para.paragraph_no + 1) if last_para else 1

    if paragraph_no >= 11:
        if debug:
            print(f"[11번째 문단 요청 거부] paragraph_no: {paragraph_no}")
        return {
            "input": user_input,
            "paragraph_text": "동화가 이미 완성되었습니다. 새로운 이야기를 원하시면 새로 시작해주세요.",
            "question": "",
            "choices": [],
            "mood": mood,
            "context": context,
            "paragraph_no": paragraph_no,
            "story_completed": True
        }

    story_substage = get_story_substage(paragraph_no)

    current_idx = paragraph_no - 1
    plan_summary = story_plan[current_idx] if story_plan and current_idx < len(story_plan) else ""
    next_summary = story_plan[current_idx + 1] if story_plan and current_idx + 1 < len(story_plan) else None

    paragraph_hint = get_paragraph_hint(story_substage)
    force_final_ending_instruction = get_force_final_ending_instruction(story_substage, paragraph_no)
    substage_instruction = get_substage_instruction(story_substage)


    # Chain of Thought 기반 사고 흐름 유도
    reasoning_instruction = (
        "Before writing the paragraph, think step-by-step:")
    reasoning_prompt = (
        "1. What just happened in the story?"
        "2. How would the character logically feel now?"
        "3. What event could naturally happen next, based on the child's input?"
        "4. What emotional tone fits best?"
        "→ Think through this, then write the paragraph.")


    # 마지막 문단 강제 종료 지침
    if paragraph_no == 10:
        instruction_suffix = (
            "- This is the final paragraph. Only write the [문장] section with 3–6 complete, emotionally conclusive sentences.\n"
            "- DO NOT write any [질문] or [행동] sections.\n"
            "- DO NOT include the [문장] label. Only provide 3–6 full sentences as natural story narration.\n"
            "- End with a warm and clear sentence that signals the story has finished.\n"
            "- Examples: 행복하게 살았답니다. / 여기서 끝이랍니다. / 어떻게 되었을까요? \n"
        )
    elif paragraph_no == 9:
        instruction_suffix = (
            "- You MUST include [문장], [질문], and [행동].\n"
            "- In the [문장], give a clear sense that the story is nearing its conclusion.\n"
            "- Use soft emotional reflection and prepare the child for closure.\n"
            "- You must gently prepare the child for the ending in the next (10th) paragraph.\n"
        )
    else: # 1~8 paragraph
        instruction_suffix = (
            "- You MUST include [문장], [질문], and [행동].\n"
            "- The [행동] MUST reflect the current story substage and help transition to the next stage.\n"
            "- Choices must align with the planned story arc (기1-기2-승1-승2-승3-전1-전2-결1-결2-에필로그).\n"
        )

    system_instruction = (
        f"You are a professional Korean children's story writer.\n\n"
        "Your tone should be warm, gentle, and immersive, like reading a picture book aloud to a child.\n"
        f"Use simple, age-appropriate language for a child aged {user_age}.\n"
        "Dialogue between close friends may use soft casual endings like ~해/~지?, but keep it warm and polite.\n"
        "- NEVER use emojis, markdown, or sound effects.\n"
        "- DO NOT repeat the stage summary or previously told story.\n"
        "- DO NOT give human names to animal or fantasy characters.\n"
        "- Do NOT assign the same name to more than one character, even if they are different species.\n"
        "- Each character must have a unique name.\n"
        "- Maintain a consistent naming convention throughout the story.\n"
        "- Encourage the child to imagine or choose the next step using the provided [질문] and [행동] sections."
    )

    user_request = (
        f"Child's New Input:\n\"{user_input}\"\n\n"
        "→ This is a NEW event or suggestion from the child.\n"
        "→ You MUST reflect this in the story continuation.\n"
        "→ Treat this input as the most recent plot development after the story so far.\n"
        "→ DO NOT ignore or skip this input.\n\n"

        f"Theme: {theme}\n"
        f"Mood: {mood}\n"
        f"Child Age: {user_age}세\n"
        f"Story Substage: '{story_substage}'\n\n"

        "--- STAGE FLOW CONTEXT ---\n\n"
        "Stage Summary (Current Step):\n"
        f"{plan_summary if plan_summary else '요약 없음'}\n\n"
        "Next Stage Goal (Guidance):\n"
        f"{next_summary if next_summary else 'N/A'}\n\n"

        f"Paragraph Hint: {paragraph_hint}\n"
        f"Substage-Specific [행동] Guidance:\n{substage_instruction}\n\n"
        f"Current Context:\n{context}\n\n"


        f"{reasoning_instruction}\n{reasoning_prompt}\n\n"


        f"Then write:\n"

        "--- INSTRUCTION ---\n\n"
        "Use the following format:\n"
        "[문장] - Continue the story in 3–6 Korean sentences.\n"
        "[질문] - Ask ONE child-directed question in Korean about what should happen next.\n"
        "[행동] - List 3 clear action choices the child can select. Each must be a full sentence.\n\n"

        "Mandatory Tone Requirements:\n"
        "- [문장]: End every sentence with ~해요/~어요/~예요/~이에요/~답니다\n"
        "- [질문]: Must end with ~을까요?/~까요?/~어요?\n"
        "- [행동]: Each choice must end with ~해요/~어요/~예요\n"
        "- DO NOT use ~았다/~었다/~했다 ANYWHERE\n\n"
        "✓ Correct Examples: (DO NOT repeat in output, just for style understanding):\n"
        "- 토끼가 숲속을 뛰어다녀요 (✅ OK)\n"
        "- 공주가 \"안녕하세요\"라고 말해요 (✅ OK)\n"
        "- 그들은 행복하게 살아요 (✅ OK)\n"
        "- 문이 열려요 (✅ OK)\n"
        "❌ DO NOT write: 뛰어다녔다, 말했다, 살았다, 열렸다\n\n"

        "Additional Formatting Constraints:\n"
        "- DO NOT phrase choices as questions or suggestions (e.g., '~할까요?', '~볼래요?').\n"
        "- Choices must describe what the character does, not what the child should do.\n"
        "- NEVER use emojis, markdown, or sound effects.\n"
        "- DO NOT repeat the story summary or previous context.\n\n"

        "Character Naming Rules:\n"
        "- Animal or fantasy characters (e.g., talking dogs, fairies, goblins) must NEVER have human names.\n"
        "- Only human characters may have Korean names\n"
        "- Each character must have a unique name across the entire story.\n\n"

        f"{instruction_suffix}"
    )

    contents = [
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        {"role": "model", "parts": [{"text": "이해했습니다. 사고 흐름을 먼저 생각한 후, 문단을 쓰겠습니다."}]},
        {'role': 'user', 'parts': [{'text': user_request}]}
    ]

    response = model.generate_content(contents)
    full_text = response.text.strip()

    paragraph, question, choices = extract_choice(full_text)

    if debug:
        print("\n" + "="*40)
        print("3. [GenerateParagraph] DEBUG LOG")
        print("="*40)
        print(f"문단 번호: {paragraph_no} / 이야기 단계: {story_substage}")
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
