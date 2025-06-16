# LangGraph 분기 함수들 관리
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15
from typing import Literal
from api.models import Story

# ------------------------------------------------------------------------------------------
# 흐름 분기 관련 함수
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: story_plan(스토리 요약)이 있는지 확인하여 RetrieveContext 또는 GenerateStoryPlan로 분기
# 마지막 수정일: 2025-06-12
def summary_router(state: dict) -> str:
    if "story_plan" in state and state["story_plan"]:
        return "RetrieveContext"
    return "GenerateStoryPlan"


# 작성자: 최준혁
# 기능: mode 값에 따라 "SaveParagraph" 또는 "UpdateParagraphVersion" 노드로 분기
# 마지막 수정일: 2025-06-03
def mode_router(state: dict) -> str:
    if state.get("mode") == "edit":
        return "UpdateParagraphVersion"
    else:
        return "SaveParagraph"

# 작성자: 최준혁
# 기능: continue_story 값에 따라 "GenerateParagraph" 또는 "__end__" 노드로 분기
# 마지막 수정일: 2025-06-11
def check_continue_or_end_router(state: dict) -> str:
    return "__end__" if state.get("paragraph_no", 1) >= 10 else "RetrieveContext"


# 작성자: 최준혁
# 기능: 이미지 생성 여부에 따라 다음 노드를 결정하는 분기 함수
# 마지막 수정일: 2025-06-08
def image_prompt_router(state: dict) -> str:
    return "GenerateImage" if state.get("generate_image") else "SaveParagraph" if state["mode"] == "create" else "UpdateParagraphVersion"

# 작성자: 최준혁
# 기능: 동화 마무리 노드로 이동하는 함수
# 마지막 수정일: 2025-06-15
def finalize_router(state: dict) -> str:
    if state.get("paragraph_no", 1) >= 10:  # 또는 your_end_condition
        return "FinalizeStory"
    return "__end__"


# 작성자: 최준혁
# 기능: 시작 노드, Story 객체 캐싱으로 DB 중복 조회 방지
# 마지막 수정일: 2025-06-16
def passthrough_start(state: dict) -> dict:    
    story_id = state.get("story_id")
    if not story_id:
        return state

    try:
        # Story 객체를 한 번만 조회하여 state에 저장 (캐싱)
        from api.models import Story
        story = Story.objects.get(story_id=story_id)
        
        # 기존 summary_4step이 있으면 state에 주입
        cached_state = {**state, "story": story}  # Story 객체 캐싱
        
        if story.summary_4step:
            print("[Start] DB 요약을 state에 주입합니다.")
            cached_state["story_plan"] = story.summary_4step.strip().splitlines()
            
        return cached_state
        
    except Exception as e:
        print(f"[Start] Story 객체 로드 실패: {e}")
        return state
