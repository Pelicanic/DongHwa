# LangGraph 노드 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
import google.generativeai as genai
import os

from api.models import Paragraphqa, Storyparagraph, Paragraphversion
from django.utils import timezone



# Gemini 초기화 및 모델 정의
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# 작성자 : 최준혁
# 기능 : 사용자 입력을 받아 동화 패러그래프를 생성하는 노드
# 마지막 수정일 : 2025-06-03
def generate_paragraph(state: dict) -> dict:
    user_input = state.get("input")
    user_age = state.get("age")

    # Gemini에게 프롬프트 전송
    prompt = (
    "아래 사용자의 요청을 바탕으로 사용자의 연령에 따라 친근한 말투를 사용하며 동화의 문장을 만들어줘.\n"
    "- 대화 상호작용을 통해 동화의 문단을 만들고, 사용자의 요청에 따라 동화의 내용을 수정해줘.\n"
    "- 사용자의 연령에 따라 문장의 길이와 복잡도를 조절해줘.\n"
    f"- 사용자의 연령은 {user_age}세.\n"
    "- 문장은 짧고 이해하기 쉽게 써줘.\n"
    "- 총 3~5문장 정도가 적당해.\n"
    "- 너무 무겁거나 복잡한 표현은 피하고, 동심을 담아줘.\n\n"
    f"사용자 요청: {user_input}"
)

    response = model.generate_content(prompt)
    generated_paragraph = response.text.strip()

    return {
        "input": user_input,
        "age": user_age,
        "paragraph_text": generated_paragraph
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

    return {
        **state,
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

    return state


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
        **state,
        "version_no": next_version
    }
