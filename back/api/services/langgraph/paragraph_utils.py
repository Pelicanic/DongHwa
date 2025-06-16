# 문단 저장 및 버전 관리 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

from api.models import Storyparagraph, Paragraphversion, Paragraphqa
from django.utils import timezone
from api.services.vector_utils import index_paragraphs_to_faiss

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

# 디버깅 설정
debug = True

# ------------------------------------------------------------------------------------------
# 문단 저장 
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 생성된 패러그래프를 StoryParagraph 테이블에 저장
# 마지막 수정일: 2025-06-03
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
        story_id=story_id,
        paragraph_no=paragraph_no,
        content_text=paragraph_text,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # ParagraphVersion 저장(v1)
    Paragraphversion.objects.create(
        paragraph_id=paragraph.paragraph_id,
        version_no=1,
        content_text=paragraph_text,
        generated_by=str(state.get("user_id")),
        created_at=timezone.now()
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


# ------------------------------------------------------------------------------------------
# 버전 관리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 기존 paragraph_id의 문단 내용을 수정하여 ParagraphVersion에 새 버전을 추가하고,
# 마지막 수정일: 2025-06-03
def update_paragraph_version(state: dict) -> dict:
    paragraph_id = state.get("paragraph_id")
    new_text = state.get("paragraph_text")
    user_id = state.get("user_id")
    question = state.get("question")

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
        "version_no": next_version,
        "question": question
    }
 

# ------------------------------------------------------------------------------------------
# QA 저장
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 사용자 입력과 패러그래프를 ParagraphQA에 저장
# 마지막 수정일: 2025-06-03
def save_qa(state: dict) -> dict:

    Paragraphqa.objects.create(
        paragraph_id=state.get("paragraph_id"),
        story_id=state.get("story_id"),
        question_text=state.get("input"),
        answer_text=state.get("paragraph_text"),
        created_at=timezone.now(),
        ai_question=state.get("question")
    )

    if debug:
        print("\n" + "-"*40)
        print("5. [SaveQA] DEBUG LOG")
        print("-"*40)
        print(f"Paragraph ID : {state['paragraph_id']}")
        print(f"Question     : {state['input']}")
        print(f"Answer Text  :\n{state['paragraph_text']}")
        print(f"Question     : {state['question']}")
        print("-"*40 + "\n")
    
        print("\n--- [SaveQA] State 확인 ---")
        for k, v in state.items():
            print(f"{k}: {v}")

    return {
        "paragraph_id": state["paragraph_id"],
        "paragraph_text": state["paragraph_text"],
        "input": state["input"]
    }
