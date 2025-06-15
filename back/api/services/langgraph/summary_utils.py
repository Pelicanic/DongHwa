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
    extract_new_characters, get_character_description, filter_significant_characters,
    get_similar_name, is_duplicate_character, renumber_characters
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
# 마지막 수정일: 2025-06-15 (리팩토링: 현재 문단 등장 인물 기반, 고정 인물 강제 포함 + 중복 판단 개선)
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

    story = Story.objects.filter(story_id=story_id).first()
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

    protagonist_name = None
    if prev_char_map:
        protagonist_name = list(prev_char_map.keys())[0]

    raw_names = extract_new_characters(paragraph_text + "\n" + user_input, list(prev_char_map.keys()))
    current_names = filter_significant_characters(paragraph_text, raw_names, user_input)

    if not current_names:
        if debug:
            print("[DetectUpdate] No valid new characters found.")
        return {**state, "characters": list(prev_char_map.values())}

    if debug:
        print(f"[DetectUpdate] New characters detected: {current_names}")

    updated_characters = []

    for name in current_names:
        if name in prev_char_map:
            updated_characters.append(prev_char_map[name])
        else:
            similar_name = get_similar_name(name, list(prev_char_map.keys()))
            if similar_name:
                updated_characters.append(prev_char_map[similar_name])
            else:
                desc = get_character_description(name, paragraph_text, user_input, age, list(prev_char_map.values()))
                if desc and not is_duplicate_character(name, desc, list(prev_char_map.values())):
                    prev_char_map[name] = desc
                    updated_characters.append(desc)
                else:
                    if debug:
                        print(f"[중복 제거됨] '{name}'은 유사한 기존 캐릭터로 간주되어 추가되지 않음.")

    if protagonist_name and protagonist_name not in [re.split(r"[:：]", line)[0].split(".", 1)[-1].strip() for line in updated_characters]:
        if protagonist_name in prev_char_map:
            updated_characters.insert(0, prev_char_map[protagonist_name])

    renumbered_characters = []
    seen_names = set()
    for line in updated_characters:
        name = re.split(r"[:：]", line)[0].split(".", 1)[-1].strip()
        if name not in seen_names:
            seen_names.add(name)
            cleaned = re.sub(r"^\d+\.\s*", "", line)
            renumbered_characters.append(f"{len(renumbered_characters)+1}. {cleaned}")

    story.characters = "\n".join(renumbered_characters)

    new_summary = None
    if paragraph_no < 9 and story.summary_4step:
        existing_lines = story.summary_4step.strip().splitlines()

        system_instruction = (
            f"You are a professional children's story writer for age {age}.\n"
            "Your task is to revise the existing 4-step story summary based on a new character input.\n"
            "Preserve the structure and flow. Reflect meaningful characters only. Do NOT invent."
            "**The output MUST be written in Korean only. DO NOT use English.**"
        )

        user_request = (
            f"[Existing Summary]\n" + "\n".join(existing_lines) + "\n\n"
            f"[Mood]: {mood}\n"
            f"[Theme]: {theme}\n"
            f"[User Input]: {user_input}\n"
            f"[Visible Characters]: {', '.join(current_names)}\n\n"
            "Output 4 numbered lines only."
            "**Write in Korean only. Do NOT use English.**"
        )

        contents = [
            {'role': 'user', 'parts': [{'text': system_instruction}]},
            {'role': 'model', 'parts': [{'text': "Understood."}]},
            {'role': 'user', 'parts': [{'text': user_request}]}
        ]

        response = model.generate_content(contents)
        raw = [line.strip() for line in response.text.strip().splitlines() if re.match(r"^\d+\.\s", line)]
        if len(raw) >= 4:
            new_summary = raw[:4]
            story.summary_4step = "\n".join(new_summary)

    story.save()

    if debug:
        print("\n" + "-" * 40)
        print("4. [DetectUpdate] DEBUG LOG")
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
    if new_summary and new_summary != "\n".join(state.get("story_plan", [])):
        new_state["story_plan"] = new_summary

    return new_state


# ------------------------------------------------------------------------------------------
# 스토리 종료 관리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 이야기 종료를 위해 paragraph_no가 10이상이면 False, 아니면 True 반환
# 마지막 수정일: 2025-06-11
def check_continue_or_end(state: "StoryState") -> dict:
    if state.get("paragraph_no", 1) >= 10:
        return {**state, "continue_story": False}
    return {**state, "continue_story": True}
