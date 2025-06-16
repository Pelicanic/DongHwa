import os
import requests
from dotenv import load_dotenv

# API 키 로드
load_dotenv(dotenv_path="C:/ai_exam/voice_practice/clogen_v2/.env")
CSS_API_CLIENT_ID = os.getenv("CSS_API_CLIENT_ID")
CSS_API_CLIENT_SECRET = os.getenv("CSS_API_CLIENT_SECRET")

def synthesize_clova_tts(
    text,
    speaker="vgoeun",
    emotion=0,
    emotion_strength=1,
    pitch=0,
    speed=0,
    volume=0,
    output_path="output.wav"
):
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": CSS_API_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CSS_API_CLIENT_SECRET
    }

    data = {
        "speaker": speaker,
        "text": text,
        "emotion": emotion,
        "emotion-strength": emotion_strength,
        "pitch": pitch,
        "speed": speed,
        "volume": volume,
        "format": "wav",
        "sampling-rate": 24000
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"❌ Clova TTS 실패: {response.status_code} - {response.text}")
        return False
