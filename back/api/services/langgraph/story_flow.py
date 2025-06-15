# LangGraph 플로우 정의
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15 (리팩토링 완료)

from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Annotated

# 리팩토링된 모듈들 import
from .core_nodes import generate_story_plan, retrieve_context, generate_paragraph
from .summary_utils import detect_and_update_story
from .paragraph_utils import save_paragraph, update_paragraph_version, save_qa
from .image_utils import generate_image
from .finalize_utils import finalize_story_output
from .routers import (
    summary_router, mode_router, check_continue_or_end_router,
    image_prompt_router, finalize_router, passthrough_start
)


class StoryState(TypedDict, total=False):
    """
    상태를 정의하는 클래스
    LangGraph 실행 중 상태(state)에 저장/전달되는 키와 타입을 명시
    작성자: 최준혁
    마지막 수정일: 2025-06-08
    """
    story_plan: Annotated[list[str], "static"]# 기승전결 요약
    input: str                                # 사용자 입력 문장
    user_id: Annotated[int, "static"]         # 사용자 ID (고정값으로 반복 허용)
    story_id: Annotated[int, "static"]        # 대상 동화 ID (고정값으로 반복 허용)
    age: Annotated[int, "static"]             # 사용자 연령 (고정값으로 반복 허용)
    paragraph_id: int                         # 단락 ID (수정 시 필요)
    paragraph_no: int                         # 단락 번호
    paragraph_text: str                       # 생성된 패러그래프 텍스트
    version_no: int                           # 버전 번호 (수정 시 증가)
    mode: Literal["create", "edit", "start", "end"]  # 생성 모드 or 수정 모드
    theme: Annotated[str, "static"]           # 대분류 (고정값으로 반복 허용)
    mood: str                                 # 분위기 
    image_required: bool                      # 이미지 필요 여부
    image_url: str                            # 이미지 URL
    continue_story: bool                      # 계속 생성할지 여부
    context: str                              # 벡터 DB에서 불러온 문맥 (RetrieveContext)


def story_flow():
    """
    LangGraph 플로우 정의 함수
    각 노드를 순서대로 등록하고, 조건에 따라 분기되도록 그래프 구성
    작성자: 최준혁
    마지막 수정일: 2025-06-15 (리팩토링 완료)
    """
    graph = StateGraph(StoryState)

    # 노드 등록
    # ------------------------------------------------------------------------

    # 시작 노드
    graph.add_node("Start", passthrough_start)

    # 1. 기승전결 요약 생성
    graph.add_node("GenerateStoryPlan", generate_story_plan)

    # 2. 이전 문단 기억 
    graph.add_node("RetrieveContext", retrieve_context)

    # 3. 문단 생성
    graph.add_node("GenerateParagraph", generate_paragraph)

    # 4. 문단 저장 
    graph.add_node("SaveParagraph", save_paragraph)

    # 5. 변경 사항이 있을 시 Story 테이블의 characters와 summary_4step 업데이트
    graph.add_node("DetectAndUpdateStory", detect_and_update_story)

    # 6. 문단 수정
    graph.add_node("UpdateParagraphVersion", update_paragraph_version)

    # 7. QA에 기록
    graph.add_node("SaveQA", save_qa)

    # 8. 이미지 생성 
    graph.add_node("GenerateImage", generate_image)

    # 9. 동화 마무리
    graph.add_node("FinalizeStory", finalize_story_output)

    # 엣지 설정
    # ------------------------------------------------------------------------

    # 1. 요약 생성, 요약이 없으면 RetrieveContext로 이동
    graph.set_entry_point("Start")
    graph.add_conditional_edges("Start", summary_router)
    graph.add_edge("GenerateStoryPlan", "RetrieveContext")

    # 2. 이전 문단 기억 -> 문단 생성
    graph.add_edge("RetrieveContext", "GenerateParagraph")

    # 3. 문단 생성 or 문단 수정 분기
    graph.add_conditional_edges("GenerateParagraph", mode_router)

    # 4. 문단 저장 후 등장인물/요약 업데이트
    graph.add_edge("SaveParagraph", "DetectAndUpdateStory")
    graph.add_edge("UpdateParagraphVersion", "DetectAndUpdateStory")  

    # 5. Detect 후 QA 저장
    graph.add_edge("DetectAndUpdateStory", "SaveQA")

    # 6. 이미지 생성 판단
    graph.add_edge("SaveQA", "GenerateImage")

    # 7. 이미지 생성 후 종료 판단
    graph.add_conditional_edges("GenerateImage", finalize_router)

    # 8. 동화 마무리
    graph.set_finish_point("FinalizeStory")

    return graph.compile()


# 플로우 다이어그램:
# Start
#   ↓
# GenerateStoryPlan
#    ├── (story_plan 있음) → RetrieveContext
#    └── (없음)            → GenerateParagraph
#         ↓
# RetrieveContext
#   ↓
# GenerateParagraph
#    ├── mode == "create" → SaveParagraph
#    └── mode == "edit"   → UpdateParagraphVersion
#         ↓
# SaveParagraph / UpdateParagraphVersion
#   ↓
# DetectAndUpdateStory
#   ↓
# SaveQA
#   ↓
# GenerateImage
#    ├── paragraph_no < 10 → __end__
#    └── paragraph_no ≥ 10 → FinalizeStory
#                              ↓
#                            [END]
