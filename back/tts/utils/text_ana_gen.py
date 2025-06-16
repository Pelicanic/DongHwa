import os
import re
import ast
import difflib
from dotenv import load_dotenv
import google.generativeai as genai

# 환경변수 로딩
load_dotenv(dotenv_path="C:/ai_exam/voice_practice/clogen_v2/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 허용된 화자 목록
VALID_SPEAKERS = {"vara", "vmikyung", "vdain", "vyuna", "vgoeun", "vdaeseong"}

def get_closest_valid_speaker(speaker_name):
    """
    잘못된 화자 이름을 가장 유사한 VALID_SPEAKER로 교체
    """    
    matches = difflib.get_close_matches(speaker_name, VALID_SPEAKERS, n=1)
    return matches[0] if matches else "vgoeun"

def analyze_texts_with_gemini(sentences):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    prompt = f"""
You are given a list of Korean sentences for speech synthesis.

For each sentence, classify whether it's narration or a character's dialogue,
and assign appropriate voice parameters accordingly.

🎙️ Speaker options:
- Narration: vmikyung or vgoeun
- Dialogues:
  - vara: Calm adult female
  - vmikyung: Middle-aged energetic female
  - vdain: Child female
  - vyuna: Teen female
  - vgoeun: Friendly adult female
  - vdaeseong: Calm adult male

🎭 Emotion: 0 (neutral), 1 (sad), 2 (happy), 3 (angry)  
🔥 Emotion Strength: 0 (weak), 1 (normal), 2 (strong)

🎚️ Volume: -5 to +5  
- -5 = quiet, 0 = normal, 5 = loud  
- Emotionally intense sentences may benefit from higher volume

🎼 Pitch: -5 (highest), 0 (normal), 5 (lowest)  
⏱️ Speed: -5 (2x faster), 0 (normal), 10 (2x slower)

📦 Return your results as a JSON array:
[
  {{
    "sentence": "text",
    "speaker": "vgoeun",
    "emotion": 2,
    "emotion_strength": 1,
    "pitch": 0,
    "speed": -2,
    "volume": 1
  }},
  ...
]

Now analyze the following sentences and return the JSON array only:
{sentences}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        print("\n📤 Gemini 응답 원문:")
        print(response_text)

        match = re.search(r"\[\s*{.*?}\s*\]", response_text, re.DOTALL)
        if match:
            json_data = match.group()
            print("\n✅ 추출된 JSON 데이터:")
            print(json_data)

            parsed = ast.literal_eval(json_data)
            print("\n🔎 분석된 결과:")

            for cfg in parsed:
                original_speaker = cfg["speaker"]
                if original_speaker not in VALID_SPEAKERS:
                    corrected = get_closest_valid_speaker(original_speaker)
                    print(f"⚠️ 잘못된 화자 이름 발견: {original_speaker} → 가장 유사한 '{corrected}'으로 교정")
                    cfg["speaker"] = corrected

                print(f"📌 '{cfg['sentence']}' → speaker: {cfg['speaker']}, emotion: {cfg['emotion']}, strength: {cfg['emotion_strength']}, pitch: {cfg['pitch']}, speed: {cfg['speed']}, volume: {cfg['volume']}")
            return parsed
        else:
            print("⚠️ 유효한 JSON 배열을 응답에서 찾을 수 없습니다.")
            raise ValueError("No valid JSON array found in Gemini response.")

    except Exception as e:
        print("❌ Gemini response parsing failed:", e)
        print("⚠️ 기본값으로 모든 문장을 처리합니다.")
        fallback = [{
            "sentence": s,
            "speaker": "vgoeun",
            "emotion": 0,
            "emotion_strength": 1,
            "pitch": 0,
            "speed": 0,
            "volume": 0
        } for s in sentences]

        for cfg in fallback:
            print(f"⚠️ 기본값 적용: '{cfg['sentence']}' → speaker: {cfg['speaker']}, emotion: {cfg['emotion']}, strength: {cfg['emotion_strength']}, pitch: {cfg['pitch']}, speed: {cfg['speed']}, volume: {cfg['volume']}")

        return fallback
