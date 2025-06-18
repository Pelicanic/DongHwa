# back/tts/main.py
import os
import time
from .utils.text_processor import split_text_into_sentences
from .utils.text_ana_gen import analyze_texts_with_gemini
from .utils.clova_tts import synthesize_clova_tts
from pydub import AudioSegment

def build_final_audio(text, save_path, gemini_api_key, clova_client_id, clova_client_secret, character_list=""):
    """
    전체 텍스트 입력 → 문단별 문장 분리 → 감정 분석 → TTS 생성
    → 병합 저장 (userID_storyID_all.mp3) → 문단별 추출 (userID_storyID_paragraph_x.mp3) → 임시파일 삭제
    """
    total_start = time.time()

    # 사용자 및 스토리 ID 추출
    base_dir = os.path.dirname(save_path)
    filename = os.path.splitext(os.path.basename(save_path))[0]
    file_prefix = filename if not filename.endswith("_all") else filename[:-4]  

    all_audio_path = os.path.join(base_dir, f"{file_prefix}_all.mp3")

    # 이미 생성된 전체 파일이 있다면 재사용
    if os.path.exists(all_audio_path):
        print(f"⚠️ 이미 존재하는 파일: {all_audio_path} → 재생성 생략")
        paragraph_paths = {}
        for i in range(10):
            para_path = os.path.join(base_dir, f"{file_prefix}_paragraph_{i + 11}.mp3")
            if os.path.exists(para_path):
                paragraph_paths[i + 11] = para_path
        return all_audio_path, paragraph_paths

    # 문단별 텍스트 추출
    paragraphs = text.strip().split("\n")

    # 문단별 문장 분리 
    paragraph_sentence_map = []
    for para in paragraphs:
        sentence_list = split_text_into_sentences(para)
        paragraph_sentence_map.append(sentence_list)

    # 전체 문장 리스트 + 문단별 인덱스 범위 생성
    all_sentences = []
    index_ranges = []
    cursor = 0
    for sents in paragraph_sentence_map:
        all_sentences.extend(sents)
        index_ranges.append(list(range(cursor, cursor + len(sents))))
        cursor += len(sents)

    print(f"✅ 전체 문장 수: {len(all_sentences)}")

    print("🔍 감정 분석 중...")
    configs = analyze_texts_with_gemini(
        all_sentences,
        api_key=gemini_api_key,
        characters=character_list
    )

    print("🎙️ TTS 합성 시작...")
    temp_dir = os.path.join(base_dir, "_segments")
    os.makedirs(temp_dir, exist_ok=True)

    segment_files = []
    durations = []

    for i, cfg in enumerate(configs):
        temp_path = os.path.join(temp_dir, f"seg_{i+1}.wav")
        print(f"   - [{i+1}] speaker={cfg['speaker']}, emotion={cfg['emotion']}")

        success = synthesize_clova_tts(
            text=cfg["sentence"],
            speaker=cfg["speaker"],
            emotion=cfg["emotion"],
            emotion_strength=cfg["emotion_strength"],
            pitch=cfg["pitch"],
            speed=cfg["speed"],
            volume=cfg["volume"],
            output_path=temp_path,
            client_id=clova_client_id,
            client_secret=clova_client_secret
        )
        if success:
            segment_files.append(temp_path)
            durations.append(len(AudioSegment.from_wav(temp_path)))

    if not segment_files:
        print("❌ TTS 합성에 성공한 파일이 없어 병합을 건너뜁니다.")
        return False

    # 병합
    print("🎧 음성 병합 중...")
    segments = [AudioSegment.from_wav(f) for f in segment_files]
    combined = sum(segments[1:], segments[0])
    combined.export(all_audio_path, format="mp3")
    audio_merge_end = time.time()
    print(f"✅ 병합 완료 및 {all_audio_path} 저장")

    # Offset 계산
    offsets = []
    current_offset = 0
    for dur in durations:
        offsets.append((current_offset, current_offset + dur))
        current_offset += dur

    # 문단 번호 1~10에 매핑
    full_audio = AudioSegment.from_mp3(all_audio_path)
    paragraph_paths = {}

    for i, idx_range in enumerate(index_ranges, start=1):
        para_path = os.path.join(base_dir, f"{file_prefix}_paragraph_{i}.mp3")
        if os.path.exists(para_path):
            print(f"⏩ 문단 {i} 파일 존재함 → 건너뜀")
            paragraph_paths[i] = para_path
            continue

        start = offsets[idx_range[0]][0]
        end = offsets[idx_range[-1]][1]
        segment = full_audio[start:end]
        segment.export(para_path, format="mp3")
        paragraph_paths[i] = para_path

    segment_split_end = time.time()

    # 임시파일 삭제
    for f in segment_files:
        try:
            os.remove(f)
        except OSError as e:
            print(f"⚠️ 임시파일 삭제 실패: {e.filename} - {e.strerror}")
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    print(f"✅ 최종 저장 완료: {all_audio_path}")
    print(f"⏱️ 전체 병합 시간: {round(audio_merge_end - total_start, 2)}초")
    print(f"⏱️ 문단별 분할 시간: {round(segment_split_end - audio_merge_end, 2)}초")
    print(f"⏱️ 총 소요 시간: {round(segment_split_end - total_start, 2)}초")

    return all_audio_path, paragraph_paths
