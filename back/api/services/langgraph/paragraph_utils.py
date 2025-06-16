# 문단 저장 및 버전 관리 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

from api.models import Storyparagraph, Paragraphversion, Paragraphqa
from django.utils import timezone
from api.services.relational_utils import index_paragraphs_to_db

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
        index_paragraphs_to_db(story_id, [paragraph_text])
    except Exception as e:
        if debug:
            print(f"[RelationalDB] 인덱싱 실패: {e}")

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
# 기능: 사용자 입력과 패러그래프를 ParagraphQA에 저장 (대량 데이터 대비 bulk_create 지원)
# 마지막 수정일: 2025-06-16
def save_qa(state: dict) -> dict:
    """
    개별 QA 저장 함수
    향후 대량 QA 생성 시 bulk_save_qa() 함수 사용 권장
    """
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


# 작성자: 최준혁
# 기능: 대량 QA 일괄 저장 함수 (향후 확장용)
# 마지막 수정일: 2025-06-16
def bulk_save_qa(qa_list: list[dict]) -> int:
    """
    여러 QA를 일괄 저장하는 함수 (성능 최적화용)
    
    Args:
        qa_list: [{
            "paragraph_id": int,
            "story_id": int, 
            "question_text": str,
            "answer_text": str,
            "ai_question": str
        }, ...]
    
    Returns:
        int: 생성된 QA 개수
    """
    if not qa_list:
        return 0
        
    qa_objects = [
        Paragraphqa(
            paragraph_id=qa["paragraph_id"],
            story_id=qa["story_id"],
            question_text=qa["question_text"],
            answer_text=qa["answer_text"],
            created_at=timezone.now(),
            ai_question=qa.get("ai_question", "")
        )
        for qa in qa_list
    ]
    
    result = Paragraphqa.objects.bulk_create(qa_objects)
    
    if debug:
        print(f"[BulkSaveQA] {len(result)}개 QA 일괄 저장 완료")
    
    return len(result)
