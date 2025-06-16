# back/tts/views.py

import os
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

# ✅ .env 파일 값을 읽기 위해 decouple의 config를 임포트합니다.
from decouple import config

from api.models import Story, Storyparagraph
from tts.main import build_final_audio
from member.authentication import CustomJWTAuthentication

@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_story_audio(request):
    user = request.user

    story_id = request.data.get("story_id")
    if not story_id:
        return Response({"error": "story_id가 필요합니다."}, status=400)

    try:
        story = Story.objects.get(story_id=story_id)
    except Story.DoesNotExist:
        return Response({"error": "해당 스토리를 찾을 수 없습니다."}, status=404)

    if story.author_user.user_id != user.user_id:
        return Response({"error": "본인의 스토리만 음성 생성이 가능합니다."}, status=403)

    paragraphs = Storyparagraph.objects.filter(story=story).order_by("paragraph_no")
    if not paragraphs.exists():
        return Response({"error": "이 스토리는 아직 문단이 없습니다."}, status=400)

    file_name = f"tts_user{user.user_id}_story{story.story_id}.mp3"
    output_path = os.path.join(settings.MEDIA_ROOT, "tts", file_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "tts", file_name))
        return Response({"message": "기존 TTS 파일 반환", "audio_url": audio_url})

    full_text = "\n".join([p.content_text for p in paragraphs if p.content_text])

    if not full_text.strip():
        return Response({"error": "음성으로 변환할 텍스트가 없습니다."}, status=400)

    # ✅ --- 이 부분을 수정합니다 ---
    try:
        # .env 파일에서 직접 API 키들을 읽어옵니다.
        gemini_tts_key = config('GEMINI_TTS_API_KEY')
        clova_id = config('CSS_API_CLIENT_ID')
        clova_secret = config('CSS_API_CLIENT_SECRET')

        success = build_final_audio(
            text=full_text,
            save_path=output_path,
            gemini_api_key=gemini_tts_key,
            clova_client_id=clova_id,
            clova_client_secret=clova_secret
        )
    except Exception as e:
        # .env 파일에 키가 없거나 다른 예외 발생 시 처리
        print(f"‼️ TTS 처리 중 예외 발생: {e}")
        return Response({"error": "TTS 생성 중 서버 내부 오류가 발생했습니다."}, status=500)
    # --- 여기까지 수정 ---

    if not success:
        return Response({"error": "TTS 생성에 실패했습니다."}, status=500)

    audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "tts", file_name))
    return Response({"message": "TTS 생성 완료", "audio_url": audio_url})

