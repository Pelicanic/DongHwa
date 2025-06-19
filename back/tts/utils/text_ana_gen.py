# back/tts/utils/text_ana_gen.py

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
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    # 디버깅 로그
    print("\n" + "="*50)
    print("🤖 [analyze_texts_with_gemini] 디버깅 시작 🤖")
    print(f"[디버그] 전달받은 캐릭터 목록:\n{characters if characters else '캐릭터 정보 없음'}")
    print("="*50)

    prompt = f"""
You are an expert voice director for a children's story speech synthesis.
For each sentence below, analyze it within the context of the story and assign the most appropriate voice parameters based on the Clova Voice API.

Character List:
{characters if characters else "No character information available."}

🎙️ Speaker Guidelines:
- Use calm adult voices (e.g., "vmikyung", "vgoeun") for narration.
- Use expressive, age-appropriate voices for dialogue:
  - "vara": Calm and kind adult female voice
  - "vmikyung": Trustworthy and energetic middle-aged female voice
  - "vdain": Lively and lovely child female voice
  - "vyuna": Cheerful and polite teenage female voice
  - "vgoeun": Calm and friendly adult female voice
  - "vdaeseong": Calm and reliable adult male voice

🎭 Emotion: 0 (neutral), 1 (sad), 2 (happy), 3 (angry)
🔥 Emotion Strength: 0 (weak), 1 (normal), 2 (strong)
🎚️ Volume: -5 to +5
🎼 Pitch: -5 (higher) to +5 (lower)
⏱️ Speed: -5 (faster) to +10 (slower)

**Rules:**
- Do NOT merge or combine any input sentences.
- Generate exactly one JSON entry per input sentence, preserving the original order.

📦 JSON array format:
[
  {{
    "sentence": "text",
    "speaker": "vgoeun",
    "emotion": 0,
    "emotion_strength": 1,
    "pitch": 0,
    "speed": 0,
    "volume": 0
  }},
  ...
]

Now analyze the following sentences and return the JSON array ONLY:
{sentences}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        print("\n📤 Gemini 응답 원문:")
        print(response_text)

        # JSON 블록 추출
        json_str = None
        if "```json" in response_text:
            match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text)
            if match:
                json_str = match.group(1)
        else:
            match = re.search(r"(\[[\s\S]*\])", response_text)
            if match:
                json_str = match.group(1)

        if not json_str:
            raise ValueError("No valid JSON array found in Gemini response.")

        parsed = json.loads(json_str)

        # 부족분 기본값으로 채워서 길이 맞추기
        if len(parsed) != len(sentences):
            print(f"⚠️ 반환된 설정 개수({len(parsed)})가 문장 수({len(sentences)})와 다릅니다. 부족분을 기본값으로 채웁니다.")
            # 부족한 항목 추가
            for idx in range(len(parsed), len(sentences)):
                parsed.append({
                    "sentence": sentences[idx],
                    "speaker": "vgoeun",
                    "emotion": 0,
                    "emotion_strength": 1,
                    "pitch": 0,
                    "speed": 0,
                    "volume": 0
                })
            # 과도한 항목은 잘라내기
            if len(parsed) > len(sentences):
                parsed = parsed[:len(sentences)]

        # 결과 디버깅 및 화자 교정
        print("\n🔎 분석된 결과:")
        for cfg in parsed:
            sp = cfg.get("speaker", "vgoeun")
            if sp not in VALID_SPEAKERS:
                corrected = get_closest_valid_speaker(sp)
                print(f"⚠️ 잘못된 화자 이름: {sp} → {corrected}")
                cfg["speaker"] = corrected
            print(f"📌 '{cfg.get('sentence')}' → speaker: {cfg['speaker']}, emotion: {cfg.get('emotion')}, pitch: {cfg.get('pitch')}")

        return parsed

    except Exception as e:
        print(f"❌ Gemini 오류: {e}")
        print("⚠️ 기본값으로 모든 문장을 처리합니다.")
        # fallback 생성
        fallback = []
        for s in sentences:
            fallback.append({
                "sentence": s,
                "speaker": "vgoeun",
                "emotion": 0,
                "emotion_strength": 1,
                "pitch": 0,
                "speed": 0,
                "volume": 0
            })
        for cfg in fallback:
            print(f"⚠️ 기본값: '{cfg['sentence']}' → speaker: {cfg['speaker']}")
        return fallback
