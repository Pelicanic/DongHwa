# 이미지 생성 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import google.generativeai as genai
import os
from api.models import Illustration
from django.utils import timezone
from api.services.langgraph.node_img import generate_image_unified

# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------------------------------------------------------------------
# 이미지 생성
# ------------------------------------------------------------------------------------------

# 작성자 : 최재우
# 기능 : 이미지 생성 노드 (성능 최적화: 2회 API 호출 → 1회 API 호출)
# 마지막 수정일 : 2025-06-16
def generate_image(state: dict) -> dict:
    # 통합 이미지 생성 함수 사용 (성능 최적화)
    imageLC = generate_image_unified(
        story_id=state.get("story_id"),
        paragraph_id=state.get("paragraph_id"),
        data=state.get("data", ""),
        check="illustration",
    )


    Illustration.objects.create(
        story_id=state.get("story_id"),
        paragraph_id=state.get("paragraph_id"),
        image_url= "test.png",
        caption_text=imageLC.get("caption_text"),
        labels=imageLC.get("labels"),
        created_at=timezone.now()
    )

    # 디버깅용
    if debug:
        print(f"5. [GenerateImage] 이미지 : caption: {imageLC.get('caption_text')}, labels: {imageLC.get('labels')}")

    return {
        "image_url": "test.png",
        "caption_text": imageLC.get('caption_text'),
        "labels": imageLC.get('labels')
    }
    

