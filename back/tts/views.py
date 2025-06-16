# back/tts/views.py

import os
import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from decouple import config

from api.models import Story, Storyparagraph, Paragraphqa # ✅ Paragraphqa 모델을 임포트합니다.
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

@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def stream_qa_audio(request, qa_id):
    """
    ParagraphQA의 ai_question을 Clova TTS를 통해 스트리밍 방식으로 전송합니다.
    """
    try:
        # 1. URL로부터 받은 qa_id로 DB에서 해당 질문 객체를 찾습니다.
        qa_instance = Paragraphqa.objects.get(qa_id=qa_id)

        # 2. (보안) 요청한 사용자가 해당 이야기의 저자인지 확인합니다.
        if qa_instance.story.author_user.user_id != request.user.user_id:
            return Response({"error": "이 이야기의 질문을 들을 권한이 없습니다."}, status=403)

        # 3. 음성으로 변환할 텍스트를 가져옵니다.
        text_to_speak = qa_instance.ai_question
        if not text_to_speak or not text_to_speak.strip():
            return Response({"error": "음성으로 변환할 질문 텍스트가 없습니다."}, status=400)

        # 4. .env 파일에서 직접 Clova API 키를 읽어옵니다.
        clova_id = config('CSS_API_CLIENT_ID')
        clova_secret = config('CSS_API_CLIENT_SECRET')

        # 5. Clova Voice API에 스트리밍 요청을 보낼 준비를 합니다.
        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": clova_id,
            "X-NCP-APIGW-API-KEY": clova_secret,
        }
        # 간단하게 읽어주는 기능이므로, 기본 화자와 옵션만 설정합니다.
        data = {
            "speaker": "vgoeun",
            "text": text_to_speak,
            "format": "mp3",
        }
        
        # 6. stream=True 옵션으로 Clova에 요청을 보내고, 응답을 실시간으로 받습니다.
        response_from_clova = requests.post(url, headers=headers, data=data, stream=True)

        # 7. Clova API의 응답이 성공적인지 확인합니다.
        if response_from_clova.status_code == 200:
            # 8. StreamingHttpResponse를 통해 클라이언트에게 오디오 데이터를 실시간으로 전달합니다.
            response = StreamingHttpResponse(
                response_from_clova.iter_content(chunk_size=4096), # 4KB씩 조각내어 전달
                content_type=response_from_clova.headers['Content-Type']
            )
            return response
        else:
            # Clova API에서 에러가 발생한 경우, 해당 내용을 로그로 남기고 클라이언트에게 에러를 알립니다.
            error_text = response_from_clova.text
            print(f"❌ Clova API Error: {response_from_clova.status_code} - {error_text}")
            return Response({"error": "음성 합성 서버에서 오류가 발생했습니다."}, status=502)

    except Paragraphqa.DoesNotExist:
        return Response({"error": "해당 질문을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        print(f"‼️ 스트리밍 처리 중 예외 발생: {e}")
        return Response({"error": "서버 내부 오류가 발생했습니다."}, status=500)