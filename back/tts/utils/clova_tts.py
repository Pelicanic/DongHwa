# back/tts/utils/clova_tts.py
import requests

def synthesize_clova_tts(
    text,
    speaker="vgoeun",
    emotion=0,
    emotion_strength=1,
    pitch=0,
    speed=0,
    volume=0,
    output_path="output.wav",
    client_id=None,
    client_secret=None
):
    """
    Clova TTS API를 호출하여 음성 합성 결과를 output_path로 저장합니다.
    """
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
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
