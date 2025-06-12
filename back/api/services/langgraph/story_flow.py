# LangGraph 플로우 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03
from langgraph.graph import StateGraph
from api.models import Story
from typing import TypedDict, Literal, Annotated, Tuple
from api.services.langgraph.nodes import (
    generate_story_plan,            # 1. Gemini로 4단계 요약 생성
    retrieve_context,               # 2. 문단 기억 처리
    generate_paragraph,             # 3. Gemini로 문단 생성
    save_paragraph,                 # 3. 문단 저장
    update_paragraph_version,       # 4. 기존 문단 수정 및 버전 추가
    save_qa,                        # 5. 사용자 입력과 응답을 QA 테이블에 저장
    generate_image,                 # 이미지 생성
    # check_continue_or_end,          # 이야기 종료 판단
)
# from api.services.langgraph.node_img import generate_image

# ------------------------------------------------------------------------
# 상태 정의
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 상태를 정의하는 클래스
#       LangGraph 실행 중 상태(state)에 저장/전달되는 키와 타입을 명시
# 마지막 수정일 : 2025-06-08
class StoryState(TypedDict, total=False):
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

# ------------------------------------------------------------------------
# 흐름 분기 관련 함수
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 흐름 분기 함수
#       story_plan(스토리 요약)이 있는지 확인하여 RetrieveContext 또는 GenerateStoryPlan로 분기
# 마지막 수정일 : 2025-06-12
def summary_router(state: dict) -> str:
    if "story_plan" in state and state["story_plan"]:
        return "RetrieveContext"
    return "GenerateStoryPlan"


# 작성자 : 최준혁
# 기능 : 흐름 분기 함수
#       mode 값에 따라 "SaveParagraph" 또는 "UpdateParagraphVersion" 노드로 분기
# 마지막 수정일 : 2025-06-03
def mode_router(state: StoryState) -> str:
    if state.get("mode") == "edit":
        return "UpdateParagraphVersion"
    else:
        return "SaveParagraph"

# 작성자 : 최준혁
# 기능 : 흐름 분기 함수
#       continue_story 값에 따라 "GenerateParagraph" 또는 "__end__" 노드로 분기
# 마지막 수정일 : 2025-06-11
def check_continue_or_end_router(state: "StoryState") -> str:
    return "__end__" if state.get("paragraph_no", 1) >= 10 else "RetrieveContext"


# 작성자 : 최준혁
# 기능 : 이미지 생성 여부에 따라 다음 노드를 결정하는 분기 함수
# 마지막 수정일 : 2025-06-08
def image_prompt_router(state: dict) -> str:
    return "GenerateImage" if state.get("generate_image") else "SaveParagraph" if state["mode"] == "create" else "UpdateParagraphVersion"


# 작성자 : 최준혁
# 기능 : 시작 노드
#       입력된 state를 그대로 반환
# 마지막 수정일 : 2025-06-12
def passthrough_start(state: dict) -> dict:
    from api.models import Story

    story_id = state.get("story_id")
    if not story_id:
        return state

    try:
        story = Story.objects.get(story_id=story_id)
        if story.summary_4step:
            print("[Start] DB 요약을 state에 주입합니다.")
            return {
                **state,
                "story_plan": story.summary_4step.strip().splitlines()
            }
    except Story.DoesNotExist:
        print(f"[Start] story_id={story_id}가 존재하지 않음")

    return state


# ------------------------------------------------------------------------
# LangGraph 플로우 정의
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : LangGraph 플로우 정의 함수
#       각 노드를 순서대로 등록하고, 조건에 따라 분기되도록 그래프 구성
# 마지막 수정일 : 2025-06-08 (ver. 현재 구현 기준)
def story_flow():
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

    # 5. 문단 수정
    graph.add_node("UpdateParagraphVersion", update_paragraph_version)

    # 6. QA에 기록
    graph.add_node("SaveQA", save_qa)

    # 7. 이미지 생성 
    graph.add_node("GenerateImage", generate_image)

    # 💤 이야기 종료 판단 (미구현)
    # graph.add_node("CheckContinueOrEnd", check_continue_or_end)

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

    # 4. 문단 저장
    graph.add_edge("GenerateParagraph", "SaveParagraph")
    # graph.add_edge("GenerateParagraph", "UpdateParagraphVersion")

    # 5. 문단 저장 후 QA에 기록
    graph.add_edge("SaveParagraph", "SaveQA")
    graph.add_edge("UpdateParagraphVersion", "SaveQA")

    # 6. 이미지 생성 판단
    graph.add_edge("SaveQA", "GenerateImage")
    # graph.add_edge("GenerateImage", "CheckContinueOrEnd")

    # 💤  이야기 종료 판단
    # graph.add_conditional_edges("CheckContinueOrEnd", check_continue_or_end_router)
    # graph.add_conditional_edges("GenerateImage", mode_router)

    # 💤  이미지 생성 이후 저장 분기
    # graph.add_edge("GenerateImage", "SaveParagraph")
    # graph.add_edge("GenerateImage", "UpdateParagraphVersion")

    # ✅ 임시 종료점 (컨텍스트, 반복 흐름 미사용 시)
    graph.set_finish_point("SaveQA")
    # graph.set_finish_point("__end__")
    # graph.set_finish_point("GenerateImage")

    return graph.compile()


# Start
#   ↓
# RetrieveContext
#   ↓
# GenerateParagraph
#   ├── create → SaveParagraph
#   └── edit   → UpdateParagraphVersion
#   ↓
# SaveQA
#   ↓
# GenerateImage
#   ↓
# CheckContinueOrEnd
#   ├── paragraph_no < 10 → RetrieveContext
#   └── paragraph_no ≥ 10 → __end__