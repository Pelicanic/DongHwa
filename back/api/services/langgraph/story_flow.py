# LangGraph 플로우 정의
# 작성자 : 최준혁
# 작성일 : 2025-06-03

from langgraph.graph import StateGraph
from typing import TypedDict, Literal, Annotated
from api.services.langgraph.nodes import (
    generate_paragraph,             # Gemini로 문단 생성
    save_paragraph,                 # 신규 문단 저장
    save_qa,                        # 사용자 입력과 응답을 QA 테이블에 저장
    update_paragraph_version,       # 기존 문단 수정 및 버전 추가
    image_prompt_check,             # 이미지 판단
    generate_image,                 # 이미지 생성
    retrieve_context,               # 컨텍스트 벡터 처리
    # index_to_vector_db,             # 컨텍스트 벡터 처리
    # check_continue_or_end,          # 루프 제어
    # check_continue_or_end_router,   # 루프 제어
)


# 작성자 : 최준혁
# 기능 : 상태를 정의하는 클래스
#       LangGraph 실행 중 상태(state)에 저장/전달되는 키와 타입을 명시
# 마지막 수정일 : 2025-06-08
class StoryState(TypedDict, total=False):
    input: str                     # 사용자 입력 문장
    user_id: Annotated[int, "static"]         # 사용자 ID (고정값으로 반복 허용)
    story_id: Annotated[int, "static"]        # 대상 동화 ID (고정값으로 반복 허용)
    age: Annotated[int, "static"]             # 사용자 연령 (고정값으로 반복 허용)
    paragraph_id: int              # 단락 ID (수정 시 필요)
    paragraph_no: int              # 단락 번호
    paragraph_text: str            # 생성된 패러그래프 텍스트
    version_no: int                # 버전 번호 (수정 시 증가)
    mode: Literal["create", "edit", "start", "end"]  # 생성 모드 or 수정 모드
    theme: Annotated[str, "static"]          # 대분류 (고정값으로 반복 허용)
    mood: str                      # 분위기 
    image_required: bool           # 이미지 필요 여부
    image_url: str                 # 이미지 URL
    continue_story: bool           # 계속 생성할지 여부
    context: str                   # 벡터 DB에서 불러온 문맥 (RetrieveContext)



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
# 마지막 수정일 : 2025-06-08 (ver. 현재 구현 기준)

def story_flow():
    graph = StateGraph(StoryState)

# 노드 등록
# ------------------------------------------------------------------------
    # ✅ 컨텍스트 벡터 처리
    graph.add_node("RetrieveContext", retrieve_context)

    # ✅ 기본 문단 생성
    graph.add_node("GenerateParagraph", generate_paragraph)

    # ✅ 이미지 생성 판단 및 생성
    graph.add_node("ImagePromptCheck", image_prompt_check)
    graph.add_node("GenerateImage", generate_image)

    # ✅ 패러그래프 저장
    graph.add_node("SaveParagraph", save_paragraph)
    graph.add_node("UpdateParagraphVersion", update_paragraph_version)
    graph.add_node("SaveQA", save_qa)

    # 💤 컨텍스트 벡터 검색 및 저장 (미구현)
    # graph.add_node("IndexToVectorDB", index_to_vector_db)

    # 💤 루프 분기 (미구현)
    # graph.add_node("CheckContinueOrEnd", check_continue_or_end)

# 엣지 설정
# ------------------------------------------------------------------------

    # 시작점 설정: ✅ RetrieveContext가 먼저 실행되어야 문맥을 프롬프트에 반영 가능
    graph.set_entry_point("RetrieveContext")
    graph.add_edge("RetrieveContext", "GenerateParagraph")

    # ✅ 생성 or 수정 분기
    graph.add_conditional_edges("GenerateParagraph", mode_router)

    # ✅ 이미지 필요 판단 후 분기
    graph.add_edge("GenerateParagraph", "ImagePromptCheck")
    # graph.add_conditional_edges("ImagePromptCheck", image_prompt_router)

    # ✅ 이미지 생성 이후 저장 분기
    graph.add_edge("GenerateImage", "SaveParagraph")
    graph.add_edge("GenerateImage", "UpdateParagraphVersion")

    # ✅ 저장 후 QA 기록
    graph.add_edge("SaveParagraph", "SaveQA")
    graph.add_edge("UpdateParagraphVersion", "SaveQA")

    # 저장 후 QA -> context 처리
    # graph.add_edge("SaveQA", "RetrieveContext")
    # graph.add_edge("RetrieveContext", "GenerateParagraph")

    # 💤 컨텍스트 흐름 (미구현)
    # graph.add_edge("SaveQA", "RetrieveContext")
    # graph.add_edge("RetrieveContext", "IndexToVectorDB")
    # graph.add_edge("IndexToVectorDB", "CheckContinueOrEnd")
    # graph.add_conditional_edges("CheckContinueOrEnd", check_continue_or_end_router)

    # ✅ 임시 종료점 (컨텍스트, 반복 흐름 미사용 시)
    graph.set_finish_point("SaveQA")

    return graph.compile()



# # 작성자 : 최준혁
# # 기능 : LangGraph 플로우 정의 함수
# #       각 노드를 순서대로 등록하고, 조건에 따라 분기되도록 그래프 구성
# # 마지막 수정일 : 2025-06-08
# def story_flow():
#     graph = StateGraph(StoryState)
    
# # 노드 등록
# # ------------------------------------------------------------------------
#     # 기본 생성 
#     graph.add_node("GenerateParagraph", generate_paragraph)

#     # 이미지 판단 및 생성
#     graph.add_node("ImagePromptCheck", image_prompt_check)
#     graph.add_node("GenerateImage", generate_image)

#     # 저장 처리
#     graph.add_node("SaveParagraph", save_paragraph)
#     graph.add_node("UpdateParagraphVersion", update_paragraph_version)
#     graph.add_node("SaveQA", save_qa)

#     # 컨텍스트 벡터 처리 (🛠️ 추후 구현 예정)
#     # graph.add_node("RetrieveContext", retrieve_context)
#     # graph.add_node("IndexToVectorDB", index_to_vector_db)

#     # 루프 제어 노드 (🛠️ 추후 구현 예정)
#     # graph.add_node("CheckContinueOrEnd", check_continue_or_end)

# # 엣지 설정
# # ------------------------------------------------------------------------

#     # 시작점 설정
#     graph.set_entry_point("GenerateParagraph")

#     # 분기: 생성 vs 수정
#     graph.add_conditional_edges("GenerateParagraph", mode_router)

#     # 이미지 판단 분기 (🛠️ 추후 조건 분기로 전환 예정)
#     # graph.add_conditional_edges("ImagePromptCheck", image_prompt_router)

#     # 이미지 생성 후 저장 흐름
#     graph.add_edge("GenerateImage", "SaveParagraph")
#     graph.add_edge("GenerateImage", "UpdateParagraphVersion")

#     # 저장 후 QA 처리
#     graph.add_edge("SaveParagraph", "SaveQA")
#     graph.add_edge("UpdateParagraphVersion", "SaveQA")

#     # 컨텍스트 벡터 및 루프 처리 흐름 (🛠️ 추후 활성화)
#     # graph.add_edge("SaveQA", "RetrieveContext")
#     # graph.add_edge("RetrieveContext", "IndexToVectorDB")
#     # graph.add_edge("IndexToVectorDB", "CheckContinueOrEnd")
#     # graph.add_conditional_edges("CheckContinueOrEnd", check_continue_or_end_router)

#     # 종료점 설정 (임시: SaveQA 이후 종료)
#     graph.set_finish_point("SaveQA")

#     return graph.compile()
