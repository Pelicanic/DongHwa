# back/tts/main.py
import os
import time
from collections import defaultdict
from .utils.text_processor import split_text_into_sentences
from .utils.text_ana_gen import analyze_texts_with_gemini
from .utils.clova_tts import synthesize_clova_tts
from pydub import AudioSegment

def build_final_audio(text, save_path, gemini_api_key, clova_client_id, clova_client_secret, character_list=""):
    """
    전체 텍스트 입력 → 문단별 문장 분리(매핑) → 감정 분석 → TTS 생성
    → 전체 오디오 병합(지연 포함) → 문단별 오디오 병합(매핑 기반) → 임시파일 삭제 후 반환
    """
    total_start = time.time()

    # 사용자 및 스토리 ID 추출
    base_dir = os.path.dirname(save_path)
    filename = os.path.splitext(os.path.basename(save_path))[0]
    file_prefix = filename if not filename.endswith("_all") else filename[:-4]

    all_audio_path = os.path.join(base_dir, f"{file_prefix}_all.mp3")

    # 이미 생성된 전체 파일이 있다면 기존 문단별 파일 재사용
    if os.path.exists(all_audio_path):
        print(f"⚠️ 이미 존재하는 파일: {all_audio_path} → 재사용")
        paragraph_paths = {}
        for i in range(1, 11):
            para_path = os.path.join(base_dir, f"{file_prefix}_paragraph_{i}.mp3")
            if os.path.exists(para_path):
                paragraph_paths[i] = para_path
        return all_audio_path, paragraph_paths

    # 1. 문단별 텍스트 분리
    raw_paras = text.strip().split("\n")
    paragraphs = [p for p in raw_paras if p.strip()]

    # 2. 문장-문단 매핑
    sentence_paragraph_map = []  # [(sentence, paragraph_no), ...]
    all_sentences = []
    for para_no, para in enumerate(paragraphs, start=1):
        sents = split_text_into_sentences(para)
        for sent in sents:
            sentence_paragraph_map.append((sent, para_no))
            all_sentences.append(sent)
    print(f"✅ 전체 문장 수: {len(all_sentences)}")

    # 3. 감정 및 화자 설정 생성
    print("🔍 감정 분석 중...")
    configs = analyze_texts_with_gemini(
        all_sentences,
        api_key=gemini_api_key,
        characters=character_list
    )
    if len(configs) != len(all_sentences):
        raise RuntimeError(
            f"Gemini 설정 개수 불일치: {len(configs)} vs {len(all_sentences)}"
        )

    # 4. 개별 WAV 세그먼트 생성
    print("🎙️ TTS 합성 시작...")
    temp_dir = os.path.join(base_dir, "_segments")
    os.makedirs(temp_dir, exist_ok=True)
    segment_files = []

    for idx, cfg in enumerate(configs):
        wav_path = os.path.join(temp_dir, f"seg_{idx+1}.wav")
        print(f"   - [{idx+1}] speaker={cfg['speaker']}, emotion={cfg['emotion']}")
        success = synthesize_clova_tts(
            text=cfg["sentence"],
            speaker=cfg["speaker"],
            emotion=cfg["emotion"],
            emotion_strength=cfg["emotion_strength"],
            pitch=cfg["pitch"],
            speed=cfg["speed"],
            volume=cfg["volume"],
            output_path=wav_path,
            client_id=clova_client_id,
            client_secret=clova_client_secret
        )
        if not success:
            raise RuntimeError(f"TTS 합성 실패: 문장 #{idx+1} – {cfg['sentence']}")
        segment_files.append(wav_path)

    # 5. 전체 오디오 병합 및 저장 (지연 포함)
    print("🎧 전체 오디오 병합 중 (지연 포함)...")
    segments = [AudioSegment.from_wav(p) for p in segment_files]
    pause = AudioSegment.silent(duration=900)  # 500ms pause between segments
    combined = segments[0]
    for seg in segments[1:]:
        combined += pause + seg
    combined.export(all_audio_path, format="mp3")
    print(f"✅ 전체 오디오 저장: {all_audio_path}")

    # 6. 문단별 오디오 병합 (매핑 기반)
    print("🔗 문단별 오디오 생성 중...")
    paragraph_to_idxs = defaultdict(list)
    for i, (_, p_no) in enumerate(sentence_paragraph_map):
        paragraph_to_idxs[p_no].append(i)

    paragraph_paths = {}
    for p_no, idxs in paragraph_to_idxs.items():
        para_path = os.path.join(base_dir, f"{file_prefix}_paragraph_{p_no}.mp3")
        combined_para = AudioSegment.empty()
        for i in idxs:
            combined_para += AudioSegment.from_wav(segment_files[i])
        combined_para.export(para_path, format="mp3")
        paragraph_paths[p_no] = para_path
        print(f"  - 문단 {p_no} 저장: {para_path}")

    # 7. 임시 파일 삭제
    for f in segment_files:
        try:
            os.remove(f)
        except OSError:
            pass
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    total_end = time.time()
    print(f"⏱️ 총 소요 시간: {round(total_end - total_start, 2)}초")

    return all_audio_path, paragraph_paths
