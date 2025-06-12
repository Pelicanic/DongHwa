# LangGraph 노드 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
import google.generativeai as genai
import os
import re

from typing import Tuple, List
from api.models import Story
from api.models import Paragraphqa, Storyparagraph, Paragraphversion
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

    guide = (
        "[역할]"
        f"당신은 {age}세 어린이를 위한 동화 작가입니다.\n"
        f"주어진 주제와 분위기를 기반으로, 이야기의 흐름을 4단계(기-승-전-결)로 나누어 간단하게 요약해주세요.\n"
        f"등장인물의 이름은 '{topic}' 안에서 처음 등장한 이름을 사용하고, 각 단계에 동일한 이름을 유지해야 합니다.\n"
        f"출력 형식은 아래 예시처럼 번호와 함께 텍스트만 깔끔하게 써주세요.\n\n"

        "[입력 정보]\n"
        f"- 주제: {topic}\n"
        f"- 테마: {theme}\n"
        f"- 분위기: {mood}\n\n"
        f"[출력 예시]\n"
        f"1. 기: 마을 소녀 수아는 어느 날 숲 속에서 신비한 알을 발견한다.\n"
        f"2. 승: 수아는 알을 돌보던 중 알에서 용이 깨어나고, 두려움과 호기심 사이에서 갈등한다.\n"
        f"3. 전: 마을 사람들은 용을 해치려 하고, 수아는 용을 구하기 위해 도망친다.\n"
        f"4. 결: 수아는 용과 함께 숲 속에서 살아가기로 결심하고 마을을 떠난다.\n\n"
        f"→ 꼭 위의 형식(숫자 + . + 단계 요약)으로만 출력해주세요. 제목, 설명, 마크다운, 굵은 글씨 없이 간단히!"
    )

    response = model.generate_content(guide)
    result = response.text.strip()

    # 마크다운 제거 및 요약 분리
    raw_lines = result.split("\n")
    story_plan = []
    for line in raw_lines:
        if re.match(r"^\d\.", line.strip()) or re.match(r"^\d+\s*[.)]", line.strip()):
            story_plan.append(line.strip())


    if debug:
        print("\n" + "="*40)
        print("1. [GenerateStoryPlan] DEBUG LOG")
        print("="*40)
        print(f"Story ID: {story_id}")
        for line in story_plan:
            print(f"   - {line}")
        print("="*40 + "\n")

    try:
        story = Story.objects.get(story_id=story_id)
        story.summary_4step = "\n".join(story_plan)  # TEXT 컬럼이므로 줄바꿈 포함
        story.save()
        print(f"[GenerateStoryPlan] 요약 저장 완료: story_id={story_id}")
    except Story.DoesNotExist:
        print(f"[GenerateStoryPlan] 요약 저장 실패: story_id={story_id} not found")


    return {
        **state,
        "story_plan": story_plan
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
# 마지막 수정일 : 2025-06-11
def generate_paragraph(state: dict) -> dict:
    # user_id = state.get("user_id")
    user_input = state.get("input")
    user_age = state.get("age")
    theme = state.get("theme")
    mood = state.get("mood")
    context = state.get("context")
    story_plan = state.get("story_plan", [])
    
    # 마지막 문단 번호 조회
    last_para = Storyparagraph.objects.filter(story_id=state.get("story_id")).order_by("-paragraph_no").first()
    paragraph_no = (last_para.paragraph_no + 1) if last_para else 1

    # 현재 진행 단계
    story_stage = get_story_stage(paragraph_no)

    # story_stage에 따라 story_plan에서 해당 요약 추출
    stage_to_index = {"기": 0, "승": 1, "전": 2, "결": 3}
    plan_summary = story_plan[stage_to_index[story_stage]] if len(story_plan) > stage_to_index[story_stage] else ""

    # 결말 강제 조건 추가
    force_final_ending_instruction = ""
    if story_stage == "결" and paragraph_no == 11:
        force_final_ending_instruction = (
            "\n\nFinal Ending Instruction:\n"
            "- This is the final paragraph of the story.\n"
            "- You MUST conclude the story in a clear, satisfying, and emotional way suitable for children.\n"
            "- DO NOT ask a follow-up question or provide any [행동] options.\n"
            "- Just write the final [문장] that wraps up the story completely.\n"
            "- Make sure the child understands this is the ending.\n"
        )



    # 시스템 지침을 첫 번째 사용자 메시지로 전달
    system_instruction = (
        "You are a professional Korean children's story writer. "
        "Your tone should be warm, gentle, and storytelling in style, like reading a picture book to a child.\n"
        f"Use simple and friendly sentences appropriate for a child aged {user_age}.\n"
        "NEVER use emojis, markdown, or sound effects (like '아!', '얘야').\n"
        "DO NOT repeat the summary inside the story.\n"
        "Choices must end with polite endings like ~해요 / ~어요.\n"
        "Your output must always follow the structure and constraints provided by the user."
        "Encourage the child to either pick from the choices or imagine their own path forward."
        )

    user_request = (
        f"Stage Summary:\n{plan_summary if plan_summary else '요약 없음'}\n\n"
        "Instructions:\n"
        "Use [문장], [질문], [행동] as section headers for your response.\n"
        "1. Continue the story in 3–5 sentences. Use [문장] section.\n"
        "2. Ask one Korean question in [질문] that invites the child to decide what happens next.\n"
        "3. Provide 3 distinct actions in [행동] that the child can choose from to continue the story.\n\n"
        "4. In the [행동] section, Each choice must be a clear, declarative sentence ending in '~해요' or '~어요' or '~한다', not a question like '~해 볼래요?' or '~래요?' or '~볼까요?'. Phrase the choice as the character's direct action, not as a suggestion to the child.\n"
        "5. The story's main character and the child are different; always phrase choices as suggestions **directed to the child only**, not the character.\n\n"
        

        "Context so far:\n"
        f"{context}\n\n"
        f"Theme: {theme}\n"
        f"Mood: {mood}\n"
        f"Child Age: {user_age}세\n"
        f"User Input: {user_input}\n\n"
                
        "Story Stage Guidelines:\n"
        "- '기': Introduce character, setting, and the start of a mysterious or exciting event.\n"
        "- '승': Develop the action. Show tension and attempts to resolve the problem.\n"
        "- '전': Present a dramatic turning point or crisis.\n"
        "- '결': Conclude with a satisfying, warm ending appropriate for children.\n\n"

        

        "Important:\n"
        "Your output must be in Korean only and strictly follow the format.\n"
        "Return only the story content. No explanations.\n"
        "- You MUST provide all three sections: [문장], [질문], and [행동].\n"
        "- You MUST provide 3 distinct actions in [행동] to help continue the story.\n"
        "- Even in the '전' (Climax) and '결' (Conclusion) stages, do not skip any section.\n"
        "- Exception: If this is the **10th paragraph** and the stage is **'결'**, then you MUST **not** include [질문] or [행동].\n"
        " In that case, just write a complete [문장] that clearly and beautifully finishes the story.\n\n"
        f"Story Stage: '{story_stage}'\n"
        f"{force_final_ending_instruction}"
        )

    # [최종 결과] API에 전달할 contents 리스트
    contents = [
        # 1. 시스템 지침을 'user' 역할로 전달
        {'role': 'user', 'parts': [{'text': system_instruction}]},
        # 2. 모델이 지침을 이해했다는 응답을 가정하여 추가 (대화 흐름을 위해 권장)
        {'role': 'model', 'parts': [{'text': '네, 알겠습니다. 전문적인 한국 동화 작가로서 아이의 나이에 맞춰 따뜻한 말투로 이야기를 만들겠습니다. 요청하신 형식에 맞춰 답변해 드릴게요.'}]},
        # 3. 실제 사용자 요청을 'user' 역할로 전달
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

