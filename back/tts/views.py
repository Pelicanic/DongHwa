import os
import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from decouple import config

from api.models import Story, Storyparagraph, Paragraphqa
from tts.main import build_final_audio
from member.authentication import CustomJWTAuthentication

# 1. 동화 전체를 분석하여 하나의 오디오북 파일을 생성하는 API
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
    
    # character 목록을 가져옵니다.
    character_list = story.characters

    if story.author_user.user_id != user.user_id:
        return Response({"error": "본인의 스토리만 음성 생성이 가능합니다."}, status=403)

    # 11번부터 20번까지의 문단만 불러오도록 필터 조건을 추가합니다.
    paragraphs = Storyparagraph.objects.filter(
        story=story,
        paragraph_no__gte=11,  # 11번 이상
        paragraph_no__lte=20   # 20번 이하
    ).order_by("paragraph_no")

    if not paragraphs.exists():
        return Response({"error": "해당 스토리에서 11번부터 20번까지의 문단을 찾을 수 없습니다."}, status=400)

    file_name = f"tts_user{user.user_id}_story{story.story_id}.mp3"
    output_path = os.path.join(settings.MEDIA_ROOT, "tts", file_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "tts", file_name))
        return Response({"message": "기존 TTS 파일 반환", "audio_url": audio_url})

    full_text = "\n".join([p.content_text for p in paragraphs if p.content_text])

    if not full_text.strip():
        return Response({"error": "음성으로 변환할 텍스트가 없습니다."}, status=400)

    try:
        gemini_tts_key = config('GEMINI_TTS_API_KEY')
        clova_id = config('CSS_API_CLIENT_ID')
        clova_secret = config('CSS_API_CLIENT_SECRET')
        success = build_final_audio(
            text=full_text,
            save_path=output_path,
            gemini_api_key=gemini_tts_key,
            clova_client_id=clova_id,
            clova_client_secret=clova_secret,
            character_list=character_list
        )
    except Exception as e:
        print(f"‼️ TTS 처리 중 예외 발생: {e}")
        return Response({"error": "TTS 생성 중 서버 내부 오류가 발생했습니다."}, status=500)

    if not success:
        return Response({"error": "TTS 생성에 실패했습니다."}, status=500)

    audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "tts", file_name))
    return Response({"message": "TTS 생성 완료", "audio_url": audio_url})


# 2. AI의 질문(ai_question)을 실시간 스트리밍으로 읽어주는 API
@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def stream_qa_audio(request, qa_id):
    """
    ParagraphQA의 ai_question을 Clova TTS를 통해 스트리밍 방식으로 전송합니다.
    """
    try:
        qa_instance = Paragraphqa.objects.get(qa_id=qa_id)

        if qa_instance.story.author_user.user_id != request.user.user_id:
            return Response({"error": "이 이야기의 질문을 들을 권한이 없습니다."}, status=403)

        text_to_speak = qa_instance.ai_question
        if not text_to_speak or not text_to_speak.strip():
            return Response({"error": "음성으로 변환할 질문 텍스트가 없습니다."}, status=400)

        clova_id = config('CSS_API_CLIENT_ID')
        clova_secret = config('CSS_API_CLIENT_SECRET')

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": clova_id,
            "X-NCP-APIGW-API-KEY": clova_secret,
        }
        data = {
            "speaker": "vgoeun",
            "text": text_to_speak,
            "format": "mp3",
        }
        
        response_from_clova = requests.post(url, headers=headers, data=data, stream=True)

        if response_from_clova.status_code == 200:
            response = StreamingHttpResponse(
                response_from_clova.iter_content(chunk_size=4096),
                content_type=response_from_clova.headers['Content-Type']
            )
            return response
        else:
            error_text = response_from_clova.text
            print(f"❌ Clova API Error: {response_from_clova.status_code} - {error_text}")
            return Response({"error": "음성 합성 서버에서 오류가 발생했습니다."}, status=502)

    except Paragraphqa.DoesNotExist:
        return Response({"error": "해당 질문을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        print(f"‼️ 스트리밍 처리 중 예외 발생: {e}")
        return Response({"error": "서버 내부 오류가 발생했습니다."}, status=500)