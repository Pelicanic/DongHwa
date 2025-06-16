# back/tts/utils/text_ana_gen.py

import os
import re
import json
import difflib
import google.generativeai as genai

# 허용된 화자 목록
VALID_SPEAKERS = {"vara", "vmikyung", "vdain", "vyuna", "vgoeun", "vdaeseong"}

def get_closest_valid_speaker(speaker_name):
    """유효하지 않은 화자 이름을 가장 유사한 VALID_SPEAKER로 교정"""
    matches = difflib.get_close_matches(speaker_name, VALID_SPEAKERS, n=1)
    return matches[0] if matches else "vgoeun"

def analyze_texts_with_gemini(sentences, api_key, characters=""):
    """
    Gemini를 호출하여 문장별 음성 연출 설정을 생성합니다.
    (프롬프트가 개선된 최종 버전)
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    # 캐릭터 목록 출력
    print("\n" + "="*50)
    print("🤖 [analyze_texts_with_gemini] 디버깅 시작 🤖")
    print(f"[디버그] 전달받은 캐릭터 목록:\n{characters if characters else '캐릭터 정보 없음'}")
    print("="*50)

    prompt = f"""
You are an expert voice director for a children's story speech synthesis.
For each sentence, analyze it within the context of the story and assign the most appropriate voice parameters.

[Character List]
{characters if characters else "No character information available."}


🎙️ Speaker guidelines:
- Use **calm adult voices** (e.g., "vmikyung", "vgoeun") for **narration**. This should feel like a parent or teacher reading a picture book aloud.
- Use more expressive, age-appropriate voices for **dialogue**:
  - "vara": Calm and kind adult female voice
  - "vmikyung": Trustworthy and energetic middle-aged female voice
  - "vdain": Lively and lovely child female voice
  - "vyuna": Cheerful and polite teenage female voice
  - "vgoeun": Calm and friendly adult female voice
  - "vdaeseong": Calm and reliable adult male voice

🎭 Emotion: 0 (neutral), 1 (sad), 2 (happy), 3 (angry)  
🔥 Emotion Strength: 0 (weak), 1 (normal), 2 (strong)

🎚️ Volume: -5 to +5  
🎼 Pitch: -5 to 5  
⏱️ Speed: -5 to 10

**Rules:**
1. A character MUST consistently have the same speaker throughout the story.
2. Base your decisions on the provided Character List and the context of the sentences.
3. **Role Exclusivity:** A speaker's role must be exclusive. If you use 'vmikyung' for narration, she cannot also voice a character in the same story, and vice versa. Assign one primary narrator and use other voices for characters.
4. **Character-Speaker Uniqueness:** Each character from the `[Character List]` must be assigned a unique speaker. Do not assign the same speaker to two different characters. 
5. Return your results as a JSON array ONLY. Do not add any explanation.

📦 JSON array format:
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

Now analyze the following new sentences and return the JSON array only:
{sentences}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        print("\n📤 Gemini 응답 원문:")
        print(response_text)
        
        json_str = None
        if "```json" in response_text:
            match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text)
            if match:
                json_str = match.group(1)
        else:
            match = re.search(r"(\[[\s\S]*\])", response_text)
            if match:
                json_str = match.group(1)

        if json_str:
            parsed = json.loads(json_str)

            print("\n🔎 분석된 결과:")
            for cfg in parsed:
                original_speaker = cfg.get("speaker", "vgoeun")
                if original_speaker not in VALID_SPEAKERS:
                    corrected = get_closest_valid_speaker(original_speaker)
                    print(f"⚠️ 잘못된 화자 이름 발견: {original_speaker} → '{corrected}'으로 교정")
                    cfg["speaker"] = corrected
                
                print(f"📌 '{cfg.get('sentence')}' → speaker: {cfg.get('speaker')}, emotion: {cfg.get('emotion')}, pitch: {cfg.get('pitch')}")
            return parsed
        else:
            raise ValueError("No valid JSON array found in Gemini response.")

    except Exception as e:
        print(f"❌ Gemini response parsing failed: {e}")
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
            print(f"⚠️ 기본값 적용: '{cfg.get('sentence')}' → speaker: {cfg.get('speaker')}")
        return fallback