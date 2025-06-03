# LangGraph 플로우 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03

from langgraph.graph import StateGraph
from typing import TypedDict, Literal
from api.services.langgraph.nodes import (
    generate_paragraph,             # Gemini로 문단 생성
    save_paragraph,                 # 신규 문단 저장
    save_qa,                        # 사용자 입력과 응답을 QA 테이블에 저장
    update_paragraph_version        # 기존 문단 수정 및 버전 추가
)


# 작성자 : 최준혁
# 기능 : 상태를 정의하는 클랙스
#       LangGraph 실행 중 상태(state)에 저장/전달되는 키와 타입을 명시
# 마지막 수정일 : 2025-06-03
class StoryState(TypedDict, total=False):
    input: str                     # 사용자 입력 문장
    user_id: int                   # 사용자 ID
    story_id: int                  # 대상 동화 ID
    age: int                       # 사용자 연령
    paragraph_id: int              # 단락 ID (수정 시 필요)
    paragraph_no: int              # 단락 번호
    paragraph_text: str            # 생성된 패러그래프 텍스트
    version_no: int                # 버전 번호 (수정 시 증가)
    mode: Literal["create", "edit"]  # 생성 모드 or 수정 모드


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
# 기능 : LangGraph 플로우 정의 함수
#       각 노드를 순서대로 등록하고, 조건에 따라 분기되도록 그래프 구성
# 마지막 수정일 : 2025-06-03
def story_flow():
    graph = StateGraph(StoryState)
    
    # 노드 등록
    graph.add_node("GenerateParagraph", generate_paragraph)
    graph.add_node("SaveParagraph", save_paragraph)
    graph.add_node("UpdateParagraphVersion", update_paragraph_version)
    graph.add_node("SaveQA", save_qa)

    # 시작점 설정
    graph.set_entry_point("GenerateParagraph")

    # 분기: create vs edit
    graph.add_conditional_edges("GenerateParagraph", mode_router)

    # 각각의 흐름 다음에 저장
    graph.add_edge("SaveParagraph", "SaveQA")
    graph.add_edge("UpdateParagraphVersion", "SaveQA")

    # 종료 노드 설정
    graph.set_finish_point("SaveQA")

    # 컴파일된 그래프 변환
    flow = graph.compile()    
    return flow
