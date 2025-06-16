# back/tts/utils/text_ana_gen.py

import os
import re
import ast
import difflib
import google.generativeai as genai

# 허용된 화자 목록
VALID_SPEAKERS = {"vara", "vmikyung", "vdain", "vyuna", "vgoeun", "vdaeseong"}

def get_closest_valid_speaker(speaker_name):
    """유효하지 않은 화자 이름을 가장 유사한 VALID_SPEAKER로 교정"""
    matches = difflib.get_close_matches(speaker_name, VALID_SPEAKERS, n=1)
    return matches[0] if matches else "vgoeun"

# ✅ --- 이 함수를 수정합니다 ---
# gemini_key를 직접 찾지 않고, api_key라는 인자로 받습니다.
def analyze_texts_with_gemini(sentences, api_key):
    genai.configure(api_key=api_key) # 👈 전달받은 api_key 사용
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
🎼 Pitch: -5 to 5  
⏱️ Speed: -5 to 10

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
            parsed = ast.literal_eval(json_data)

            print("\n🔎 분석된 결과:")
            for cfg in parsed:
                original_speaker = cfg["speaker"]
                if original_speaker not in VALID_SPEAKERS:
                    corrected = get_closest_valid_speaker(original_speaker)
                    print(f"⚠️ 잘못된 화자 이름 발견: {original_speaker} → '{corrected}'으로 교정")
                    cfg["speaker"] = corrected

                print(f"📌 '{cfg['sentence']}' → speaker: {cfg['speaker']}, emotion: {cfg['emotion']}, pitch: {cfg['pitch']}")

            return parsed
        else:
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
            print(f"⚠️ 기본값 적용: '{cfg['sentence']}' → speaker: {cfg['speaker']}")
        return fallback