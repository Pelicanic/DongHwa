# LangGraph 노드 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
import google.generativeai as genai
import os

from api.models import Paragraphqa, Storyparagraph, Paragraphversion
from django.utils import timezone
from api.services.vector_utils import search_similar_paragraphs
from api.services.vector_utils import index_paragraphs_to_faiss


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
# 기능 : 사용자 입력을 받아 동화 패러그래프를 생성하는 노드
# 마지막 수정일 : 2025-06-03
def generate_paragraph(state: dict) -> dict:
    user_input = state.get("input")
    user_age = state.get("age")
    theme = state.get("theme")
    mood = state.get("mood")
    context = state.get("context")

    # Gemini에게 프롬프트 전송
    prompt = (
        "아래 사용자의 요청을 바탕으로 사용자의 연령에 따라 친근한 말투를 사용하며 동화의 문장을 만들어줘.\n"
        "- 추임새를 넣지 말아줘. 어휴, 얘야, 아! 등의 추임새와 이모지 사용을 자제해줘.\n"
        "- 대화 내용 자체가 한 권의 동화책이 될 예정이기 때문에 덧붙이는 말 없이 이전 대화와 연결이 잘 되게 해줘.\n"
        "- 대화 상호작용을 통해 동화의 문단을 만들고, 사용자의 요청에 따라 동화의 내용을 수정해줘.\n"
        "- 사용자의 연령에 따라 문장의 길이와 복잡도를 조절해줘.\n"
        f"- 사용자의 연령은 {user_age}세.\n"
        f"- 대분류는 '{theme}', 분위기는 '{mood}'야.\n"
        f"- 앞서 생성된 이야기를 이어가야 해. 현재 문맥은 다음과 같아:\n{context}\n"
        "- 문장은 짧고 이해하기 쉽게 써줘.\n"
        "- 총 3~5문장 정도가 적당해.\n"
        "- 너무 무겁거나 복잡한 표현은 피하고, 동심을 담아줘.\n\n"
        f"새로운 입력: {user_input}"
    )

    if debug:
        print(f"[GenerateParagraph] prompt: {prompt}")

    response = model.generate_content(prompt)
    generated_paragraph = response.text.strip()

    return {
        "input": user_input,
        "paragraph_text": generated_paragraph,
        "mood": mood,
        "context": context
    }


# 작성자 : 최준혁
# 기능 : 벡터 DB에서 관련 문맥을 조회하여 상태에 context로 추가
def retrieve_context(state: dict) -> dict:
    query = state.get("input", "")
    story_id = state.get("story_id")

    try:
        retrieved_context = search_similar_paragraphs(story_id, query, top_k=3)
    except Exception as e:
        print(f"[RetrieveContext Error] {e}")
        retrieved_context = ""

    if not retrieved_context:
        retrieved_context = "이전에 생성된 문맥이 없습니다."

    if debug:
        print(f"[RetrieveContext] Retrieved context: {retrieved_context}")

    return {
        **state,
        "context": retrieved_context
    }


# 작성자 : 최준혁
# 기능 : 생성된 패러그래프를 StroyParagraph 테이블에 저장
#       동일한 내용을 ParagraphVersion 테이블에 v1로 저장
# 마지막 수정일 : 2025-06-03
def save_paragraph(state: dict) -> dict:
    story_id = state.get("story_id")
    paragraph_text = state.get("paragraph_text")

    # 단락 번호 계산 : 현재 story_id에서 가장 높은 번호 + 1
    last_para = Storyparagraph.objects.filter(story_id=story_id).order_by("-paragraph_no").first()
    next_no = (last_para.paragraph_no + 1) if last_para else 1

    if debug:
        print(f"[SaveParagraph] story_id: {story_id}, paragraph_text: {paragraph_text}")

    # StoryParagraph 테이블에 저장
    paragraph = Storyparagraph.objects.create(
        story_id = story_id,
        paragraph_no = next_no,
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
        "paragraph_id": paragraph.paragraph_id,
        "paragraph_no": next_no
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

    return {
        "paragraph_id": state["paragraph_id"],
        "paragraph_text": state["paragraph_text"],
        "input": state["input"]
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

    return {
        "paragraph_id": paragraph_id,
        "paragraph_text": new_text,
        "version_no": next_version
    }




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
        "다음 문단은 동화의 일부입니다. 이 문단이 시작적인 이미지로 표현하기에 적합하다면  'yes', "
        "그렇지 않다면 'no'만 출력해주세요. 다른 설명은 필요하지 않습니다. \n\n"
        f"문단 : {paragraph}"
    )

    if debug:
        print(f"[ImagePromptCheck] prompt: {prompt}")

    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        generate_image = "yes" in output
    except Exception as e:
        print(f"[ImagePromptCheck Error] {e}")
        generate_image = False

    return {
        **state,
       "image_required": generate_image
    }


# 작성자 : 최준혁
# 기능 : 이미지 생성 여부에 따라 다음 노드를 결정하는 분기 함수
# 마지막 수정일 : 2025-06-08
def image_prompt_router(state: dict) -> str:
    return "GenerateImage" if state.get("generate_image") else "SaveParagraph" if state["mode"] == "create" else "UpdateParagraphVersion"


# 작성자 : 최준혁
# 기능 : 이미지 생성 더미 노드
# 마지막 수정일 : 2025-06-08
def generate_image(state: dict) -> dict:
    theme = state.get("theme", "판타지 (SF/이세계)")
    mood = state.get("mood", "신비로운")

    labels = find_labels_by_theme_and_mood(theme, mood)

    # 디버깅용
    if debug:
        print(f"[GenerateImage] 이미지 URL: {image_url}, caption: {caption_text}")
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

