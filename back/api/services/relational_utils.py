# 관계형 DB 기반 문맥 검색 (벡터DB 대체)
# 작성자: 최준혁  
# 작성일: 2025-06-16
# 마지막 수정일: 2025-06-16

from api.models import Storyparagraph
from django.db.models import Q
import re

# ------------------------------------------------------------------------
# 관계형 DB 기반 문맥 검색 함수들
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : 관계형 DB에서 키워드 기반 문맥 검색 (벡터DB 대체)
# 마지막 수정일 : 2025-06-16
def search_similar_paragraphs_by_keywords(story_id: int, query: str, top_k: int = 4) -> str:
    """
    벡터DB 대신 관계형DB에서 키워드 매칭으로 유사한 문단 검색
    """
    if not query or not query.strip():
        return get_latest_paragraphs(story_id, top_k)
    
    try:
        # 1. 쿼리에서 의미있는 키워드 추출
        keywords = extract_meaningful_keywords(query)
        
        if not keywords:
            # 키워드가 없으면 최신 문단 반환
            return get_latest_paragraphs(story_id, top_k)
        
        # 2. 키워드 포함된 문단들 검색 (OR 조건)
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(content_text__icontains=keyword)
        
        # 3. 해당 스토리의 문단들 중에서 키워드 매칭
        matching_paragraphs = (
            Storyparagraph.objects
            .filter(story_id=story_id)
            .filter(q_objects)
            .order_by("-paragraph_no")  # 최신순으로 정렬
            [:top_k]
        )
        
        if matching_paragraphs:
            # 키워드 매칭된 문단들 반환
            context_texts = [p.content_text for p in matching_paragraphs]
            return "\n".join(context_texts)
        else:
            # 매칭되는 문단이 없으면 최신 문단들 반환
            return get_latest_paragraphs(story_id, top_k//2)  # 더 적은 수로
            
    except Exception as e:
        print(f"[DB Search] 키워드 검색 실패: {e}")
        # 실패 시 폴백으로 최신 문단 반환
        return get_latest_paragraphs(story_id, top_k//2)

def extract_meaningful_keywords(text: str) -> list[str]:
    """
    텍스트에서 의미있는 키워드 추출 (간단한 방식)
    """
    # 한글 키워드만 추출 (2-5글자)
    korean_words = re.findall(r'[가-힣]{2,5}', text)
    
    # 불용어 제거 (일반적인 단어들)
    stop_words = {
        '그런데', '하지만', '그래서', '그리고', '그때', '이때', '그것', '이것',
        '어떻게', '무엇을', '어디서', '언제', '왜', '어떤', '어느', '그런',
        '이런', '저런', '그거', '이거', '저거', '여기', '거기', '저기',
        '지금', '나중', '먼저', '다음', '다시', '또', '더', '가장',
        '정말', '너무', '매우', '아주', '조금', '많이', '빨리', '천천히'
    }
    
    # 의미있는 키워드만 필터링
    meaningful_keywords = []
    for word in korean_words:
        if (word not in stop_words and 
            len(word) >= 2 and 
            len(word) <= 5 and
            word not in meaningful_keywords):  # 중복 제거
            meaningful_keywords.append(word)
    
    # 최대 5개 키워드만 사용 (성능 고려)
    return meaningful_keywords[:5]

# 작성자: 최준혁
# 기능: 최신 문단 기준으로 최근 문단들 불러오기 (기존 함수 유지)
# 마지막 수정일: 2025-06-16
def get_latest_paragraphs(story_id: int, top_k: int = 6) -> str:
    """
    벡터 검색 대신 단순히 최신 문단들을 가져오는 함수
    """
    try:
        paragraphs = (
            Storyparagraph.objects
            .filter(story_id=story_id)
            .order_by("-paragraph_no")[:top_k]
        )
        latest_texts = [p.content_text for p in reversed(paragraphs)]  # 시간순으로 정렬
        return "\n".join(latest_texts)
    except Exception as e:
        print(f"[DB Context] 최신 문단 불러오기 실패: {e}")
        return ""

# 작성자: 최준혁  
# 기능: 벡터 인덱싱 대체 함수
# 마지막 수정일: 2025-06-16
def index_paragraphs_to_db(story_id: int, paragraphs: list[str]):
    """
    벡터 인덱싱 대체 함수 - 관계형 DB에서는 별도 인덱싱 불필요
    문단은 이미 Storyparagraph 테이블에 저장되므로 추가 작업 없음
    """
    if len(paragraphs) > 0:
        print(f"[DB Index] 문단 {len(paragraphs)}개 이미 DB에 저장됨 (인덱싱 불필요)")
    pass
