# 동화 완성 마무리 처리 관련 유틸리티 함수들
# 작성자: 최준혁
# 마지막 수정일: 2025-06-18 (Storyparagraph 제거 및 context 확인 추가)

import google.generativeai as genai
import os
from api.models import Story
from django.utils import timezone
import re

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------------------------------------------------------------------
# 동화 요약 및 마무리 (제목 + 요약만 생성)
# ------------------------------------------------------------------------------------------

def finalize_story_output(state: dict) -> dict:
    story_id = state.get("story_id")
    if not story_id:
        print("[FinalizeStory] story_id 없음")
        return state

    # 이미 완료된 스토리인지 확인
    story = state.get("story") or Story.objects.filter(story_id=story_id).first()
    if story and getattr(story, 'is_completed', False):
        print("[FinalizeStory] 이미 완료된 스토리입니다. 추가 작업을 건너뜁니다.")
        return {
            **state,
            "story_completed": True,
            "title": story.title or "완성된 동화",
            "summary_3line": story.summary or "이미 완료된 동화입니다.",
            "narrative_story": "동화가 이미 완성되었습니다.",
            "completion_message": "동화가 완성되었습니다. 새로운 이야기를 원하시면 새로 시작해주세요."
        }

    # context(전체 문단 텍스트)가 비어 있으면 중단
    full_text = state.get("context", "").strip()
    if not full_text:
        print("[FinalizeStory] ⚠️ context가 비어 있어 제목/요약 생성을 중단합니다.")
        return {
            **state,
            "story_completed": False,
            "completion_message": "본문 내용이 없어 제목과 요약을 생성할 수 없습니다."
        }

    # 프롬프트 구성
    prompt = (
        "당신은 어린이를 위한 따뜻한 동화를 쓰는 전문 작가입니다.\n"
        "다음은 아이가 직접 만든 동화 전체 문단입니다.\n"
        "이 동화를 바탕으로 다음 두 가지를 순서대로 작성해 주세요:\n\n"
        "1. 아이의 상상과 감정이 잘 담긴 감성적인 제목 (15자 이내)\n"
        "2. 어린이가 쉽게 이해할 수 있도록 3문장 이내로 요약\n"
        "출력 예시 형식:\n"
        "1. 제목: ...\n"
        "2. 요약: ...\n\n"
        "모든 출력은 한국어로 작성해 주세요.\n"
        "마크다운은 사용하지 마세요.\n"
        f"{full_text}"
    )

    # Gemini 호출
    response = model.generate_content(prompt)
    lines = response.text.strip().splitlines()

    # 제목 및 요약 추출
    def extract_section(prefixes: list[str]) -> str:
        for line in lines:
            for p in prefixes:
                if line.strip().startswith(p):
                    return line.split(":", 1)[-1].strip()
        return ""

    title = extract_section(["1.", "1. 제목", "제목"])
    summary = extract_section(["2.", "2. 요약", "요약"])

    if not title and not summary:
        print("[FinalizeStory] ❗ Gemini 응답에서 제목과 요약을 추출하지 못했습니다.")
        return {
            **state,
            "story_completed": False,
            "completion_message": "Gemini 응답에서 제목과 요약을 생성하지 못했습니다."
        }

    # DB에 저장
    if story:
        story.title = title
        story.summary = summary
        story.status = "completed"
        story.is_completed = True
        story.completed_at = timezone.now()
        story.save()

    if debug:
        print("\n" + "-" * 40)
        print("[FinalizeStory] 제목 및 요약 추출")
        print("-" * 40)
        print("Lines:")
        print(lines)
        print("Response Text:")
        print(response.text)
        print("Title:")
        print(title)
        print("Summary:")
        print(summary)
        print("-" * 40 + "\n")

    return {
        **state,
        "story_completed": True,
        "title": title,
        "summary_3line": summary,
        "completion_message": "동화가 완성되었습니다!"
    }

# ------------------------------------------------------------------------------------------
# 완료 상태 체크 및 저장 제어 유틸리티
# ------------------------------------------------------------------------------------------

def check_story_completion_before_save(story_id: str) -> bool:
    try:
        story = Story.objects.filter(story_id=story_id).first()
        return bool(story and getattr(story, 'is_completed', False))
    except:
        return False

def safe_save_paragraph(story_id: str, paragraph_data: dict) -> bool:
    if check_story_completion_before_save(story_id):
        print(f"[저장 거부] 스토리 {story_id}는 이미 완료되었습니다.")
        return False
    try:
        # Storyparagraph 제거로 인해 이 함수는 더 이상 사용되지 않지만 유지
        print("[safe_save_paragraph] 사용되지 않음 (Storyparagraph 제거됨)")
        return False
    except Exception as e:
        print(f"[저장 실패] {e}")
        return False
