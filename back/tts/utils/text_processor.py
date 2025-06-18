# back/tts/utils/text_processor.py
import kss
import re

def split_text_into_sentences(text):
    """
    입력된 텍스트를 문장 단위로 분리하되,
    큰따옴표("...") 안의 대사와 나레이션을 구분하여 분리합니다.
    """
    raw_sentences = kss.split_sentences(text)
    refined = []

    for sentence in raw_sentences:
        # 큰따옴표 기준으로 나누기 (말풍선 분리)
        parts = re.split(r'(".*?")', sentence)  # "대사" 구간만 따로 추출
        for part in parts:
            clean = part.strip()
            if clean:
                refined.append(clean)

    return refined
