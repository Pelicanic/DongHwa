# 동화 완성 마무리 처리 관련 유틸리티 함수들
# 작성자: 최준혁
# 작성일: 2025-06-03
# 마지막 수정일: 2025-06-15

import google.generativeai as genai
import os
from api.models import Story, Storyparagraph
from django.utils import timezone
import re
# ------------------------------------------------------------------------------------------
# 초기화 및 설정
# ------------------------------------------------------------------------------------------

debug = True

# Gemini 모델 초기화
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------------------------------------------------------------
# 동화 요약 및 마무리
# ------------------------------------------------------------------------------------------

# 작성자: 최준혁
# 기능: 동화의 제목을 짓고, 요약 및 전체 문단을 자연스럽게 연결한 완결형 이야기 본문을 생성
# 마지막 수정일: 2025-06-15
def finalize_story_output(state: dict) -> dict:
    story_id = state.get("story_id")
    if not story_id:
        print("[FinalizeStory] story_id 없음")
        return state

    # 1. 기존 문단 전체 불러오기
    paragraphs = (
        Storyparagraph.objects
        .filter(story_id=story_id)
        .order_by("paragraph_no")
        .values_list("content_text", flat=True)
    )
    full_text = "\n".join(paragraphs)

    # 2. 프롬프트
    prompt = (
        "당신은 어린이를 위한 따뜻한 동화를 쓰는 전문 작가입니다.\n"
        "다음은 아이가 직접 만든 동화 전체 문단입니다.\n"
        "이 동화를 바탕으로 다음 세 가지를 순서대로 작성해 주세요:\n\n"
        "1. 아이의 상상과 감정이 잘 담긴 감성적인 제목 (15자 이내)\n"
        "2. 어린이가 쉽게 이해할 수 있도록 3문장 이내로 요약\n"
        "3. 기존 문단 내용을 최대한 그대로 살리면서, 이야기가 자연스럽게 이어지도록 정리한 완결형 이야기\n"
        "   (단, 반드시 10개의 단락으로 나누어 정리하고, 각 단락은 2~4문장 정도로 구성하세요)\n\n"
        "중요한 지침:\n"
        "- 아이가 만든 문장의 표현과 흐름을 가능한 한 유지하세요.\n"
        "- 단어만 부드럽게 다듬고, 단락 사이 연결이 자연스럽도록 이어주세요.\n"
        "- 새 내용을 덧붙이거나 줄이지 말고, 아이의 상상이 잘 보존되도록 정리하세요.\n"
        "- 동화의 말투는 친절하고 따뜻하며, 아이가 듣기 좋은 말로 구성해주세요.\n"
        "- 각 단락은 다음 형식으로 구분해 주세요: [단락 1], [단락 2], ..., [단락 10]\n\n"
        "출력 예시 형식:\n"
        "1. 제목: ...\n"
        "2. 요약: ...\n"
        "3. 본문:\n"
        "[단락 1] ...\n"
        "[단락 2] ...\n"
        "...\n"
        "[단락 10] ...\n\n"
        "모든 출력은 한국어로 작성해 주세요.\n\n"
        f"{full_text}"
    )


    # 3. Gemini 호출
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    lines = response.text.strip().splitlines()

    # 4. 제목 및 요약 추출
    def extract_section(prefixes: list[str]) -> str:
        for line in lines:
            for p in prefixes:
                if line.strip().startswith(p):
                    return line.split(":", 1)[-1].strip()
        return ""

    title = extract_section(["1.", "1. 제목", "제목"])
    summary = extract_section(["2.", "2. 요약", "요약"])

    # 5. 단락 추출
    new_paragraphs = []
    capture = False
    for line in lines:
        if re.match(r"\[단락\s*\d+\]", line.strip()):
            new_paragraphs.append(line.split("]", 1)[-1].strip())
            capture = True
        elif capture and line.strip():
            new_paragraphs[-1] += " " + line.strip()

    # 6. 예외 처리: 10개 미만이면 문장 수 기준으로 재분할
    if len(new_paragraphs) < 10:
        print(f"[경고] Gemini가 반환한 단락 수: {len(new_paragraphs)} → 10개로 보정")
        full_body = "\n".join(new_paragraphs)
        sentences = re.split(r'(?<=[.?!])\s+', full_body.strip())
        chunk_size = max(1, len(sentences) // 10)
        new_paragraphs = [
            " ".join(sentences[i:i + chunk_size])
            for i in range(0, len(sentences), chunk_size)
        ][:10]  # 정확히 10개 자르기

    # 7. Story에 저장
    story = Story.objects.filter(story_id=story_id).first()
    if story:
        story.title = title
        story.summary = summary
        story.status = "completed"
        story.save()

    # 8. 기존 문단 이후 번호 기준으로 이어서 저장
    last_para = (
        Storyparagraph.objects
        .filter(story_id=story_id)
        .order_by("-paragraph_no")
        .first()
    )
    next_para_no = (last_para.paragraph_no + 1) if last_para else 1

    for i, para in enumerate(new_paragraphs):
        Storyparagraph.objects.create(
            story_id=story.story_id,
            paragraph_no=next_para_no + i,
            content_text=para.strip(),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

    print("\n" + "-" * 40)
    print("[FinalizeStory] 저장 완료")
    print(f"제목       : {title}")
    print(f"단락 개수  : {len(new_paragraphs)}")
    print("-" * 40 + "\n")

    return {
        **state,
        "title": title,
        "summary_3line": summary,
        "narrative_story": "\n\n".join(new_paragraphs)
    }
