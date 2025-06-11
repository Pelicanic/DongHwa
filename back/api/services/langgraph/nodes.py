# LangGraph 노드 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
import google.generativeai as genai
import os
import re

from typing import Tuple, List

from api.models import Paragraphqa, Storyparagraph, Paragraphversion
from django.utils import timezone
from api.services.vector_utils import search_similar_paragraphs
from api.services.vector_utils import index_paragraphs_to_faiss
from api.services.vector_utils import get_latest_paragraphs


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
# 마지막 수정일 : 2025-06-11
def generate_paragraph(state: dict) -> dict:
    # user_id = state.get("user_id")
    user_input = state.get("input")
    user_age = state.get("age")
    theme = state.get("theme")
    mood = state.get("mood")
    context = state.get("context")

    # 마지막 문단 번호 조회
    last_para = Storyparagraph.objects.filter(story_id=state.get("story_id")).order_by("-paragraph_no").first()
    paragraph_no = (last_para.paragraph_no + 1) if last_para else 1

    # 진행상태 enum 계산
    story_stage_map = {
        1: "기", 2: "기",
        3: "승", 4: "승", 5: "승",
        6: "전", 7: "전", 8: "전",
        9: "결", 10: "결"
    }

    story_stage = story_stage_map.get(paragraph_no, "기")

    # Gemini에게 프롬프트 전송
    prompt = (
        "[❗중요❗ 반드시 지켜야 할 규칙입니다.]\n"
        f"현재 진행 중인 이야기 단계는 '[진행상태] {story_stage}'입니다.\n"
        "- 오로지 '한국어'만 사용해주세요. 외국어 사용 금지. 특히 러시아어를 사용하지 마세요.\n"

        "[역할]\n"
        "당신은 아이를 위한 동화 작가입니다.\n"

        "아래 사용자의 요청을 바탕으로 이야기를 이어가는 문장을 만들어주세요.\n\n"
        "프롬프트 입력에 대해서 응답하지 말고, 아래의 형식에 따라 답변을 작성해주세요.\n\n"

        "[이야기 전개 방법]\n"
        "[질문 횟수]의 1~2회는 이야기를 시작하는 상황을 소개하고, 주인공이나 배경, 문제 등을 자연스럽게 제시해주세요."
        "[질문 횟수]의 1~2회 [문장]은 이야기를 시작하는 장면이어야 합니다."
        "[질문 횟수]의 1~2회 [질문]은 '다음에 어떤 일이 일어날까?'처럼 궁금증을 유도하세요."
        "[질문 횟수]의 1~2회 [행동]은 아이가 이야기의 방향을 처음 선택할 수 있도록 기본적인 탐색 또는 선택지 '3가지'로 구성해주세요."

        "[질문 횟수]의 3~5회는 이야기가 본격적으로 전개되어야 하며, 주인공이 무언가를 시도하거나 문제에 다가가는 흐름을 그려주세요."
        "[질문 횟수]의 3~5회 [문장]은 흥미롭게 긴장감을 높이고, 행동의 결과를 암시해주세요."
        "[질문 횟수]의 3~5회 [질문]은 '이제 무엇을 할까?','무엇을 선택할까?'처럼 주인공의 다음 행동을 묻는 형식이 좋아요."
        "[질문 횟수]의 3~5회 [행동]은 상황에 적극적으로 반응하는 선택지 '3가지'로 구성해주세요."

        "[질문 횟수]의 6~8회는 위기나 갈등의 절정을 표현해야 합니다."
        "[질문 횟수]의 6~8회 [문장]은 갈등이 심화되거나 큰 전환점이 되는 장면을 담아주세요."
        "[질문 횟수]의 6~8회 [질문]은 아이가 직접 다음 결정을 내릴 수 있도록 방향성을 주는 질문이어야 합니다."
        "[질문 횟수]의 6~8회 [행동]은 극복을 위한 전략적인 선택지 '3가지'로 구성해주세요."

        "[질문 횟수]의 9~10회는 이야기를 마무리해야 하며, 질문 없이 동화처럼 아름답고 부드럽게 끝내주세요."
        "[질문 횟수]의 9~10회 [문장]은 [문장]만 작성하고, [질문]과 [행동]은 포함하지 마세요."
        "[질문 횟수]의 9~10회 [질문]은 아이가 만족할 수 있도록 교훈, 감동, 따뜻함을 느낄 수 있는 결말이어야 합니다."

        # "[진행상태]의 '기'는 이야기를 시작하는 상황을 소개하고, 주인공이나 배경, 문제 등을 자연스럽게 제시해주세요."
        # "[진행상태]의 '기'의 [문장]은 이야기를 시작하는 장면이어야 합니다."
        # "[진행상태]의 '기'의 [질문]은 '다음에 어떤 일이 일어날까?'처럼 궁금증을 유도하세요."
        # "[진행상태]의 '기'의 [행동]은 아이가 이야기의 방향을 처음 선택할 수 있도록 기본적인 탐색 또는 선택지 '3가지'로 구성해주세요."

        # "[진행상태]의 '승'은 이야기가 본격적으로 전개되어야 하며, 주인공이 무언가를 시도하거나 문제에 다가가는 흐름을 그려주세요."
        # "[진행상태]의 '승'의 [문장]은 흥미롭게 긴장감을 높이고, 행동의 결과를 암시해주세요."
        # "[진행상태]의 '승'의 [질문]은 '이제 무엇을 할까?','무엇을 선택할까?'처럼 주인공의 다음 행동을 묻는 형식이 좋아요."
        # "[진행상태]의 '승'의 [행동]은 상황에 적극적으로 반응하는 선택지 '3가지'로 구성해주세요."

        # "[진행상태]의 '전'은 위기나 갈등의 절정을 표현해야 합니다."
        # "[진행상태]의 '전'의 [문장]은 갈등이 심화되거나 큰 전환점이 되는 장면을 담아주세요."
        # "[진행상태]의 '전'의 [질문]은 아이가 직접 다음 결정을 내릴 수 있도록 방향성을 주는 질문이어야 합니다."
        # "[진행상태]의 '전'의 [행동]은 극복을 위한 전략적인 선택지 '3가지'로 구성해주세요."

        # "[진행상태]의 '결'은 이야기를 마무리해야 하며, 질문 없이 동화처럼 아름답고 부드럽게 끝내주세요."
        # "[진행상태]의 '결'은 [문장]만 작성하고, [질문]과 [행동]은 포함하지 마세요."
        # "[진행상태]의 '결'은 아이가 만족할 수 있도록 교훈, 감동, 따뜻함을 느낄 수 있는 결말이어야 합니다."


        f"- 앞선 이야기의 흐름은 다음과 같습니다:\n{context}\n"

        "[작성 조건]\n"
        f"- 사용자의 연령은 {user_age}세이며, 연령에 맞게 쉽고 친근한 문장을 써주세요.\n"
        f"- 테마는 '{theme}', 분위기는 '{mood}'입니다.\n"
        "- 대화 전체가 한 권의 동화책처럼 자연스럽게 연결되어야 하며, 덧붙이는 설명이나 이모지는 넣지 마세요.\n"
        "- 추임새(예: 얘야, 아! 등)는 넣지 마세요.\n"
        "- 이야기 주인공과 아이는 다르니, 행동 제안 시 아이에게만 말해 주세요.\n\n"

        "[출력 형식]\n"
        "이야기를 할때 ~어, ~했어 등 아이에게 동화를 읽어주는듯한 일관된 말투를 사용해서 이야기를 진행해주세요."
        "1. 동화 이야기의 다음 '문장'을 3~5문장 이내로 작성해주세요.\n"
        "2. 위 이야기에 이어, 아이에게 다음 전개를 물어보는 '질문' '1개'를 작성해주세요. (이름을 묻지 마세요)\n"
        "3. 아이가 선택할 수 있도록, 새롭게 생성하는 이야기를 기준으로 이야기와 연결되는 '행동' 제안 반드시 '3가지'를 각각 한 문장으로 제시해주세요.\n"
        "4. [이야기 흐름]을 기억하되, [이야기 흐름]을 '행동' 제안으로 생성하면 안됩니다."
        "5. '행동' 제안은 아이가 다음 이야기를 진행하기 위해 선택하는 옵션으로, 청유형이 아닌 ~해요, ~어요 처럼 선택지로 제시해주세요.\n"
        "6. 완성된 동화는 자연스럽게 이어져야 하기 때문에, '질문' 때문에 본문의 흐름이 부자연스럽게 연결되면 안됩니다."
        "7. 질문과 답변을 참고하여 다음 전개를 이전의 문장과 자연스럽게 이어지도록 작성해주세요."
        "8. 각 파트 사이에는 구분자(예: [문장], [질문], [행동])를 넣어서 구분해주세요. 문장은 단순히 이어서 자연스럽게 쓰되 구분이 명확하게 보이게 해주세요.\n\n"


        # "[진행상태]\n"
        # "결\n"

    f"[새로운 입력]: {user_input}"
)


    response = model.generate_content(prompt)
    full_text = response.text.strip()


    paragraph, question, choices = extract_choice(full_text)


    if debug:
        print("2. [GenerateParagraph] full_text: ", full_text)
        # print(f"[GenerateParagraph] input: {user_input}")
        # print(f"[GenerateParagraph] context: {context}")
        # print(f"[GenerateParagraph] mood: {prompt}")
        # print(f"[GenerateParagraph] paragraph: {paragraph}")
        print(f"[GenerateParagraph] 카운트: {paragraph_no}")
        print(f"[GenerateParagraph] question: {question}")
        print(f"[GenerateParagraph] choices: {choices}")

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
# 기능 : Gemini의 응답을 파싱하여 문장, 질문, 선택지로 분리
# 마지막 수정일 : 2025-06-10
def extract_choice(text: str) -> Tuple[str, str, List[str]]:
    paragraph = ""
    question = ""
    choices = []

    # 각 태그를 찾는 정규표현식
    paragraph_match = re.search(r"\[문장\](.*?)(?=\[질문\]|\[행동\]|\Z)", text, re.DOTALL)
    question_match = re.search(r"\[질문\](.*?)(?=\[행동\]|\Z)", text, re.DOTALL)
    choices_match = re.findall(r"\d+\.\s*(.+)", text)

    # 추출 및 공백 정리
    if paragraph_match:
        paragraph = paragraph_match.group(1).strip()

    if question_match:
        question = question_match.group(1).strip()

    choices = [choice.strip() for choice in choices_match]

    return paragraph, question, choices



# 작성자 : 최준혁
# 기능 : 벡터 DB에서 관련 문맥을 조회하여 상태에 context로 추가
# 마지막 수정일 : 2025-06-10
def retrieve_context(state: dict) -> dict:
    query = state.get("input", "")
    story_id = state.get("story_id")

    retrieved_context = ""

    try:
        # 우선 벡터 검색 시도
        retrieved_context = search_similar_paragraphs(story_id, query, top_k=3)
        if not retrieved_context:
            print("[RetrieveContext] 벡터 검색 결과 없음. 최근 문단 사용.")
            retrieved_context = get_latest_paragraphs(story_id, top_k=3)
    except Exception as e:
        print(f"[RetrieveContext Error] {e}")
        retrieved_context = get_latest_paragraphs(story_id, top_k=3)

    if not retrieved_context:
        retrieved_context = "이전에 생성된 문맥이 없습니다."

    if debug:
        print(f"1. [RetrieveContext] Retrieved context: {retrieved_context}")

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
    # paragraph_text = state.get("paragraph_text")

    # 단락 번호 계산 : 현재 story_id에서 가장 높은 번호 + 1
    last_para = Storyparagraph.objects.filter(story_id=story_id).order_by("-paragraph_no").first()
    next_no = (last_para.paragraph_no + 1) if last_para else 1

    if debug:
        print(f"3. [SaveParagraph] story_id: {story_id}, paragraph_no: {next_no}, paragraph_text: {paragraph_text}")

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

    if debug:
        print(f"4. [SaveQA] paragraph_id: {state['paragraph_id']}, question_text: {state['input']}, answer_text: {state['paragraph_text']}")
    
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

