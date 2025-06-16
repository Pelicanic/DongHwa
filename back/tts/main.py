import os
import time
from .utils.text_processor import split_text_into_sentences
from .utils.text_ana_gen import analyze_texts_with_gemini
from .utils.clova_tts import synthesize_clova_tts
from pydub import AudioSegment


def merge_audio_files(file_list, output_name, pause_duration_ms=500):
    """여러 개의 wav 파일을 하나로 병합 (중간에 정적 pause 삽입)"""
    if not file_list:
        print("병합할 파일이 없습니다.")
        return

    # pydub이 mp3를 직접 처리하지 못하는 경우를 대비해 wav로 통일
    # 이 부분은 synthesize_clova_tts가 wav로 저장하므로 유효합니다.
    combined = AudioSegment.from_wav(file_list[0])

    for file in file_list[1:]:
        combined += AudioSegment.silent(duration=pause_duration_ms)
        combined += AudioSegment.from_wav(file)

    # 최종 저장 포맷을 mp3로 변경
    final_format = output_name.split('.')[-1]
    combined.export(output_name, format=final_format)
    print(f"✅ 병합 완료 및 {output_name} 저장")

    for file in file_list:
        try:
            os.remove(file)
        except OSError as e:
            print(f"임시 파일 삭제 오류: {e.filename} - {e.strerror}")


def build_final_audio(text, save_path, gemini_api_key, clova_client_id, clova_client_secret):
    """
    텍스트 입력 → 문장 분리 → 감정 분석 → TTS 생성 → 병합 저장
    저장 결과: save_path(mp3/wav)
    """
    start_time = time.time()

    sentences = split_text_into_sentences(text)
    print(f"✅ 분리된 문장 수: {len(sentences)}")

    print("🔍 감정 분석 중...")
    # ✅ --- 이 부분을 수정합니다 ---
    # 전달받은 gemini_api_key를 인자로 넘겨줍니다.
    configs = analyze_texts_with_gemini(sentences, api_key=gemini_api_key)

    print("🎙️ TTS 합성 시작...")
    temp_files = []

    for i, cfg in enumerate(configs):
        temp_filename = f"temp_{i+1}.wav"
        print(f"   - [{i+1}] speaker={cfg['speaker']}, emotion={cfg['emotion']}")

        success = synthesize_clova_tts(
            text=cfg["sentence"],
            speaker=cfg["speaker"],
            emotion=cfg["emotion"],
            emotion_strength=cfg["emotion_strength"],
            pitch=cfg["pitch"],
            speed=cfg["speed"],
            volume=cfg["volume"],
            output_path=temp_filename,
            client_id=clova_client_id,
            client_secret=clova_client_secret
        )
        if success:
            temp_files.append(temp_filename)

    print("🎧 음성 병합 중...")
    if temp_files:
        merge_audio_files(temp_files, save_path)
        print(f"✅ 최종 저장 완료: {save_path}  (총 {round(time.time() - start_time, 2)}초)")
        return True
    else:
        print("❌ TTS 합성에 성공한 파일이 없어 병합을 건너뜁니다.")
        return False
