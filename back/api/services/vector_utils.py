from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
import os
from api.models import Storyparagraph

VECTORDB_ROOT = './vectordb/'
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")


# ------------------------------------------------------------------------
# Vector DB관련 함수
# ------------------------------------------------------------------------

# 작성자 : 최준혁
# 기능 : DB에 저장된 문단을 받아 벡터화 및 저장
# 마지막 수정일 : 2025-06-08
def index_paragraphs_to_faiss(story_id: int, paragraphs: list[str]):
    story_path = os.path.join(VECTORDB_ROOT, f"story_{story_id}")
    os.makedirs(story_path, exist_ok=True)  # 폴더 생성

    docs = [Document(page_content=p, metadata={"story_id": story_id}) for p in paragraphs]

    if os.path.exists(os.path.join(story_path, "index.faiss")):
        vectorstore = FAISS.load_local(story_path, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(docs)
    else:
        vectorstore = FAISS.from_documents(docs, embedding=embeddings)

    vectorstore.save_local(story_path)
    print(f"[VectorStore] 저장 완료: {story_path}")


# 작성자 : 최준혁
# 기능 : 저장된 벡터 DB에서 문맥 검색
# 마지막 수정일 : 2025-06-08
def search_similar_paragraphs(story_id: int, query: str, top_k: int = 6) -> str:
    story_path = os.path.join(VECTORDB_ROOT, f"story_{story_id}")
    if not os.path.exists(os.path.join(story_path, "index.faiss")):
        print(f"[VectorStore] 경로 없음: {story_path}")
        return ""

    try:
        vectorstore = FAISS.load_local(story_path, embeddings, allow_dangerous_deserialization=True)
        docs = vectorstore.similarity_search(query, k=top_k)
        context = "\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"[VectorStore] 검색 실패: {e}")
        return ""


# 작성자: 최준혁
# 기능: 최신 문단 기준으로 최근 3개 불러오기 (벡터 검색 대체 or 보완)
# 마지막 수정일: 2025-06-10
def get_latest_paragraphs(story_id: int, top_k: int = 6) -> str:
    try:
        paragraphs = (
            Storyparagraph.objects
            .filter(story_id=story_id)
            .order_by("-paragraph_no")[:top_k]
        )
        latest_texts = [p.content_text for p in reversed(paragraphs)]  # 가장 오래된 것부터
        return "\n".join(latest_texts)
    except Exception as e:
        print(f"[RetrieveContext] 최신 문단 불러오기 실패: {e}")
        return ""