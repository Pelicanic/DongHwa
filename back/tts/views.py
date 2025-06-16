# back/tts/views.py
import os
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from api.models import Story, Storyparagraph
from tts.main import build_final_audio


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_story_audio(request):
    user = request.user
    data = request.data
    story_id = data.get("story_id")

    if not story_id:
        return JsonResponse({"error": "story_id는 필수입니다."}, status=400)

    try:
        story = Story.objects.get(story_id=story_id)
        if story.author_user.user_id != user.id:
            return JsonResponse({"error": "해당 스토리에 접근 권한이 없습니다."}, status=403)
    except Story.DoesNotExist:
        return JsonResponse({"error": "해당 story_id의 스토리를 찾을 수 없습니다."}, status=404)

    # 문단 가져오기
    paragraphs = (
        Storyparagraph.objects
        .filter(story=story)
        .order_by("paragraph_no")
        .values_list("content_text", flat=True)
    )

    if not paragraphs:
        return JsonResponse({"error": "해당 스토리에 문단이 존재하지 않습니다."}, status=400)

    full_text = "\n".join(paragraphs)

    # 저장 경로
    filename = f"tts_user{user.id}_story{story_id}.mp3"
    save_dir = os.path.join(settings.MEDIA_ROOT, "tts")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    try:
        build_final_audio(
            text=full_text,
            save_path=save_path,
            gemini_api_key=os.getenv("GEMINI_TTS_API_KEY"),
            clova_client_id=os.getenv("CSS_API_CLIENT_ID"),
            clova_client_secret=os.getenv("CSS_API_CLIENT_SECRET")
        )
    except Exception as e:
        return JsonResponse({"error": f"TTS 생성 실패: {str(e)}"}, status=500)

    audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "tts", filename))
    return JsonResponse({"message": "TTS 생성 완료", "audio_url": audio_url})
