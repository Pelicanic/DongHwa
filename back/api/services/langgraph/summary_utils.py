# 요약 흐름 관리 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import re
import google.generativeai as genai
import os
from typing import List

from api.models import Story
from .character_utils import (
    extract_and_describe, get_similar_name, is_duplicate_character
)
from .parsing_utils import is_choice_only

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------------------------------------------------------------
# 스토리 단계 관리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 기승전결 분할
# 마지막 수정일: 2025-06-12
def get_story_stage(paragraph_no: int) -> str:
    if paragraph_no <= 2:
        return "기"
    elif paragraph_no <= 5:
        return "승"
    elif paragraph_no <= 8:
        return "전"
    else:
        return "결"


# ------------------------------------------------------------------------------------------
# 스토리 업데이트 및 캐릭터 관리
# ------------------------------------------------------------------------------------------
# 작성자: 최준혁
# 기능: 사용자 입력을 통해 Story 테이블의 characters와 summary_4step을 수정하는 메인 함수
# 마지막 수정일: 2025-06-17 (10단계 요약 기반 업데이트 대응)
def detect_and_update_story(state: dict) -> dict:
    if state.get("paragraph_no", 1) == 1:
        print("[DetectUpdate] 첫 문단이므로 스킵")
        return state

    story_id = state.get("story_id")
    paragraph_text = state.get("paragraph_text", "")
    user_input = state.get("input", "")
    age = state.get("age", 7)
    mood = state.get("mood", "")
    theme = state.get("theme", "")
    paragraph_no = state.get("paragraph_no", 1)

    story = state.get("story") or Story.objects.filter(story_id=story_id).first()
    if not story:
        print(f"[DetectUpdate] story_id {story_id} not found.")
        return state

    if is_choice_only(user_input):
        print("[DetectUpdate] 선택지 입력만 포함된 것으로 판단 → 캐릭터 및 요약 업데이트 스킵")
        return {**state, "characters": story.characters.splitlines() if story.characters else []}

    prev_character_lines = story.characters.splitlines() if story.characters else []
    prev_char_map = {
        re.split(r"[:：]", line)[0].split(".", 1)[-1].strip(): line
        for line in prev_character_lines
    }
    protagonist_name = list(prev_char_map.keys())[0] if prev_char_map else None

    # 통합 캐릭터 추출
    unified_result = extract_and_describe(
        text=paragraph_text + "\n" + user_input,
        user_input=user_input,
        known_names=list(prev_char_map.keys()),
        age=age
    )
    new_characters_data = unified_result.get("new_characters", [])

    if debug:
        print(f"[DetectUpdate] New characters detected: {[c['name'] for c in new_characters_data]}")

    updated_characters = []
    for char_data in new_characters_data:
        name, description = char_data["name"], char_data["description"]
        if name in prev_char_map:
            updated_characters.append(prev_char_map[name])
        else:
            similar_name = get_similar_name(name, list(prev_char_map.keys()))
            if similar_name:
                updated_characters.append(prev_char_map[similar_name])
            else:
                next_number = len(prev_char_map) + len(updated_characters) + 1
                formatted_desc = f"{next_number}. {name} : {description}"
                if not is_duplicate_character(name, formatted_desc, list(prev_char_map.values())):
                    prev_char_map[name] = formatted_desc
                    updated_characters.append(formatted_desc)

    if protagonist_name and protagonist_name not in [re.split(r"[:：]", line)[0].split(".", 1)[-1].strip() for line in updated_characters]:
        updated_characters.insert(0, prev_char_map[protagonist_name])

    renumbered_characters, seen_names = [], set()
    for line in updated_characters:
        name = re.split(r"[:：]", line)[0].split(".", 1)[-1].strip()
        if name not in seen_names:
            seen_names.add(name)
            cleaned = re.sub(r"^\d+\.\s*", "", line)
            renumbered_characters.append(f"{len(renumbered_characters)+1}. {cleaned}")
    story.characters = "\n".join(renumbered_characters)

    # ✅ 새 요약 흐름 생성 조건: story_plan 존재 + 사용자 입력의 의미성 + paragraph_no < 10
    existing_lines = story.summary_4step.strip().splitlines() if story.summary_4step else []
    new_summary = None
    if existing_lines and user_input.strip() and paragraph_no < 10 and len(existing_lines) == 10:
        system_instruction = (
            f"You are a professional Korean children's story writer for age {age}.\n"
            "Your task is to revise the existing 10-step story outline in Korean.\n"
            "You MUST reflect the latest [사용자 입력], but ONLY to the extent that it naturally fits the story's flow and tone.\n"
            "If the input is extreme or disruptive, interpret it creatively and smoothly integrate it into the existing narrative.\n"
            "- Keep the structure: 1. 기1, 2. 기2, ..., 10. 에필로그\n"
            "- Preserve character traits and emotional flow.\n"
            "- NEVER insert disruptive or inconsistent content.\n"
            "**All output must be in Korean. Do NOT use English.**"
        )

        user_request = (
            f"[기존 요약]\n" + "\n".join(existing_lines) + "\n\n"
            f"[사용자 입력]\n{user_input}\n\n"
            f"[현재 등장인물]: {', '.join([char['name'] for char in new_characters_data])}\n"
            f"[분위기]: {mood} / [주제]: {theme}\n\n"
            "→ 위 내용을 바탕으로 10단계 요약을 새롭게 수정해주세요.\n"
            "- 각 줄은 '1. 기1: ...', '2. 기2: ...' 형식으로 시작하고, 한국어로만 작성하세요.\n"
        )

        contents = [
            {'role': 'user', 'parts': [{'text': system_instruction}]},
            {'role': 'model', 'parts': [{'text': "Understood."}]},
            {'role': 'user', 'parts': [{'text': user_request}]}
        ]

        try:
            response = model.generate_content(contents)
            raw = [line.strip() for line in response.text.strip().splitlines() if re.match(r"^\d+\. ", line)]
            if len(raw) == 10:
                new_summary = raw
                story.summary_4step = "\n".join(new_summary)
        except Exception as e:
            print(f"[DetectUpdate] 요약 업데이트 실패: {e}")

    story.save()

    if debug:
        print("\n" + "-" * 40)
        print("5. [DetectUpdate] DEBUG LOG")
        print("-" * 40)
        print(f"Story ID     : {story_id}")
        print(f"User Input   : {user_input}")
        print(f"Characters   :")
        for c in renumbered_characters:
            print(f"  {c}")
        if new_summary:
            print("Updated Summary:")
            for s in new_summary:
                print(f"  {s}")
        print("-" * 40 + "\n")

    new_state = {**state, "characters": renumbered_characters}
    if new_summary and new_summary != state.get("story_plan"):
        new_state["story_plan"] = new_summary

    return new_state


# ------------------------------------------------------------------------------------------
# 스토리 종료 관리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 이야기 종료를 위해 paragraph_no가 10이상이면 False, 아니면 True 반환
# 마지막 수정일: 2025-06-17

def check_continue_or_end(state: "StoryState") -> dict:
    if state.get("paragraph_no", 1) >= 10:
        return {**state, "continue_story": False}
    return {**state, "continue_story": True}
