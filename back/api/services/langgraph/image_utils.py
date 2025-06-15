# 이미지 생성 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import google.generativeai as genai
import os

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# 테마/분위기별 이미지 라벨 매핑
THEME_MOOD_LABELS = {
    ("로맨스", "잔잔한"): ["연인", "노을", "공원"],
    ("로맨스", "슬픈"): ["눈물", "편지", "비"],
    ("판타지", "신비로운"): ["마법", "용", "성"],
    ("SF", "긴장감"): ["우주선", "전투", "외계인"],
    ("미스터리", "긴장감"): ["탐정", "그림자", "단서"],
    ("고전", "따뜻한"): ["성", "옛날 옷", "마차"],
    # 기타 등등 추가
}


# ------------------------------------------------------------------------------------------
# 이미지 생성 판단
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 생성된 패러그래프에 따라 이미지 생성 여부를 판단
# 마지막 수정일: 2025-06-08
def image_prompt_check(state: dict) -> dict:
    paragraph = state.get("paragraph_text", "")

    prompt = (
        # 프롬프트를 강화하거나, 프론트에서 이미지 태그 트리거를(버튼?) 주거나
        "다음 문단은 동화의 일부입니다. 이 문단이 시각적인 이미지로 표현하기에 적합하다면 'yes', "
        "그렇지 않다면 'no'만 출력해주세요. 다른 설명은 필요하지 않습니다. \n\n"
        f"문단 : {paragraph}"
    )

    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        generate_image = "yes" in output
        if debug:
            print(f"[ImagePromptCheck] output: {output}")
    except Exception as e:
        print(f"[ImagePromptCheck Error] {e}")
        generate_image = False

    return {
        **state,
        "image_required": generate_image
    }


# ------------------------------------------------------------------------------------------
# 이미지 생성
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 이미지 생성 더미 노드
# 마지막 수정일: 2025-06-08
def generate_image(state: dict) -> dict:
    theme = state.get("theme", "판타지 (SF/이세계)")
    mood = state.get("mood", "신비로운")
    image_url = state.get("image_url", "")
    caption_text = state.get("caption", "")

    labels = find_labels_by_theme_and_mood(theme, mood)

    # 디버깅용
    if debug:
        print(f"5. [GenerateImage] 이미지 URL: {image_url}, caption: {caption_text}")
        print(f"[GenerateParagraph] theme: {theme}, mood: {mood}")

    return {
        "image_url": f"https://dummyimage.com/600x400/000/fff&text=Image",
        "caption": f"{theme} 테마의 {mood} 분위기를 담은 이미지",
        "labels": labels
    }


# ------------------------------------------------------------------------------------------
# 라벨 매핑
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 테마와 분위기에 따른 이미지 라벨을 찾는 함수
# 마지막 수정일: 2025-06-08
def find_labels_by_theme_and_mood(theme: str, mood: str) -> list:
    for (key_theme, key_mood), labels in THEME_MOOD_LABELS.items():
        if key_theme == theme and key_mood == mood:
            return labels
    return ["기본", "이미지", "라벨"]
