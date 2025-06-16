import os
import time
from utils.text_processor import split_text_into_sentences
from utils.text_ana_gen import analyze_texts_with_gemini
from utils.clova_tts import synthesize_clova_tts
from pydub import AudioSegment

def merge_audio_files(file_list, output_name, pause_duration_ms=500):
    if not file_list:
        print("병합할 파일이 없습니다.")
        return

    pause = AudioSegment.silent(duration=pause_duration_ms)
    combined = AudioSegment.from_wav(file_list[0])
    for file in file_list[1:]:
        combined += pause
        combined += AudioSegment.from_wav(file)

    combined.export(output_name, format="wav")

    for file in file_list:
        os.remove(file)

def main():
    text = input("📥 변환할 텍스트를 입력하세요:\n").strip()

    start_time = time.time()

    sentences = split_text_into_sentences(text)
    print("\n✅ 문장 분리 결과:")
    for i, s in enumerate(sentences, 1):
        print(f"{i}. {s}")

    print("\n🔍 Gemini로 문장 분석 중...")
    configs = analyze_texts_with_gemini(sentences)

    print("\n🎙️ Clova TTS로 음성 합성 시작...")
    temp_files = []

    for i, cfg in enumerate(configs):
        file_name = f"temp_{i+1}.wav"
        print(f"  - [{i+1}] Clova TTS 호출: speaker={cfg['speaker']}, emotion={cfg['emotion']}, strength={cfg['emotion_strength']}, pitch={cfg['pitch']}, speed={cfg['speed']}, volume={cfg['volume']}")

        success = synthesize_clova_tts(
            text=cfg["sentence"],
            speaker=cfg["speaker"],
            emotion=cfg["emotion"],
            emotion_strength=cfg["emotion_strength"],
            pitch=cfg["pitch"],
            speed=cfg["speed"],
            volume=cfg["volume"],
            output_path=file_name
        )
        if success:
            temp_files.append(file_name)

    print("\n🎧 최종 음성 병합 중...")
    merge_audio_files(temp_files, "final_output.wav")
    print("✅ 완료! 🎉 생성된 파일: final_output.wav")

    elapsed = round(time.time() - start_time, 2)
    print(f"⏱️ 전체 처리 시간: {elapsed}초")

if __name__ == "__main__":
    main()
