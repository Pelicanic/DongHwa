# 작성자 : 최재우
# 작성일 : 2025-06-11
import google.generativeai as genai
import os
import re

from typing import Tuple, List

from api.models import Paragraphqa, Storyparagraph, Paragraphversion
from api.services.vector_utils import get_latest_paragraphs
from langchain_core.prompts import PromptTemplate

debug = True

# ------------------------------------------------------------------------------------------
# Gemini 초기화 및 모델 정의
# ------------------------------------------------------------------------------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------------------------------------------------------------------
# 패러그래프 생성 관련
# ------------------------------------------------------------------------------------------

# return 값 : "paragraph_id": state["paragraph_id"], "paragraph_text": state["paragraph_text"], "input": state["input"]

def generate_image(state: dict) -> dict:
    story_id = state.get("story_id")
    paragraph_id = state.get("paragraph_id")

    story_paragraph = Storyparagraph.objects.filter( paragraph_id=paragraph_id)

    print("story_paragraph======================================================",story_paragraph)

    # prompt = PromptTemplate.from_template(
    # """
    # 당신은 텍스트를 분석하여 Stable Diffusion용 이미지 생성 프롬프트를 만드는 전문가입니다.

    # 주어진 텍스트를 분석하여 다음 정보를 추출하고 최적화된 프롬프트를 생성하세요:

    # 1. **테마 분석**: 텍스트의 주요 주제와 배경
    # 2. **분위기 분석**: 감정적 톤과 분위기
    # 3. **시각적 요소**: 묘사된 장면, 캐릭터, 객체들
    # 4. **스타일 힌트**: 예술 스타일이나 시각적 특성

    # **Stable Diffusion 프롬프트 작성 규칙:**
    # - 명확하고 구체적인 시각적 설명 사용
    # - 감정과 분위기를 나타내는 형용사 포함
    # - 예술 스타일 키워드 추가 (예: "digital art", "fantasy art", "photorealistic")
    # - 품질 향상 키워드 포함 (예: "highly detailed", "8k", "masterpiece")
    # - 부정적 요소는 negative prompt로 별도 제안

    # 응답 형식:
    # ```
    # json
    # {{
    #     "theme": "추출된 테마",
    #     "mood": "추출된 분위기", 
    #     "visual_elements": ["시각적 요소1", "시각적 요소2"],
    #     "positive_prompt": "Stable Diffusion용 긍정 프롬프트",
    #     "negative_prompt": "Stable Diffusion용 부정 프롬프트",
    #     "style_tags": ["스타일 태그1", "스타일 태그2"]
    # }}
    # ```
    # """
    # )

    # chain = 


    # # illustration 테이블에 저장
    # illustration = Storyparagraph.objects.create(
    #     story_id = story_id,
    #     paragraph_id = paragraph_id,
    #     image_url = image_url,
    #     caption_text = caption_text,
    #     labels = labels,
    # )




    # theme = state.get("theme", "판타지 (SF/이세계)")
    # mood = state.get("mood", "신비로운")
    # labels = find_labels_by_theme_and_mood(theme, mood)



    # # 디버깅용
    # if debug:
    #     print(f"[GenerateImage] 이미지 URL: {image_url}, caption: {caption_text}")
    #     print(f"[GenerateParagraph] theme: {theme}, mood: {mood}")



    return {
        "image_url": f"https://dummyimage.com/600x400/000/fff&text=Image",
        "caption": f"{theme} 테마의 {mood} 분위기를 담은 이미지",
        "labels": labels
    }


# def find_labels_by_theme_and_mood(theme: str, mood: str) -> list:
#     for (key_theme, key_mood), labels in THEME_MOOD_LABELS.items():
#         if key_theme == theme and key_mood == mood:
#             return labels
#     return ["기본", "이미지", "라벨"]