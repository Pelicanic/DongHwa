# 라이브러리 불러오기
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.runnable import RunnableMap

# CSV
from langchain_community.document_loaders.csv_loader import CSVLoader

# GEMINI API KEY
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

# 전역변수
SOURCE_PATH     = './source/'
VECTORDB_PATH   = './vectordb/'

# 인베딩 모델
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07"
)
# 벡터DB 경로 변수
vectordb_qa = ''
retriever = ''
chain = ''

# 벡터디비 처리 함수
def vectordb_save(source_file):
    global embeddings

    print('-'*20)
    print('벡터디비 생성 시작')

    # 단계 1 : 문서 로드(Load Documents)
    sFile = SOURCE_PATH + source_file + '.pdf'
    # sFile = SOURCE_PATH + source_file + '.csv'
    loader = PyMuPDFLoader(sFile)
    # loader = CSVLoader(file_path=sFile)
    docs = loader.load()
    print(f"문서 페이지수 : {len(docs)}")

    # 단계 2 : 문서 분할(Split Documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=50
    )
    split_documents = text_splitter.split_documents(docs)
    print(f"분할문서 페이지수 : {len(split_documents)}")

    # 단계 3 : 임베딩 후 벡터DB로 처리하는 과정
    vectorstore = FAISS.from_documents(
        documents=split_documents,
        embedding=embeddings
    )

    # 단계 4 : 벡터 DB 저장
    vFile = VECTORDB_PATH + source_file
    print("vFile =", vFile)
    vectorstore.save_local(vFile)

    print('-'*20)
    print(f'벡터디비 생성 완료 : {vFile}')

# 벡터디비 불러오는 함수
def vectordb_load(vectordb_path):
    global vectordb_qa, embeddings, retriever, chain

    # 벡터함수를 불러오기
    vFile = VECTORDB_PATH + vectordb_path

    # try:
    vectordb_qa = FAISS.load_local(
        vFile, 
        embeddings, 
        allow_dangerous_deserialization=True)
    # except:
    #     print(f"벡터 디비 불러오기오류 : {vFile}")
    #     return False

    # 응답 및 프롬프트 구성
    retriever = vectordb_qa.as_retriever()

    # 사용자 프롬프트(프롬프트 엔지니어링)
    # 어떻게 대답할것인가 ?

    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Answer in Korean.

    #Question: 
    {question} 
    #Context: 
    {context} 

    #Answer:"""
    )

    # 채팅에 사용할 모델
    gemini = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0
    )

    # 채팅 모듈 설계
    chain = RunnableMap({
        "context": lambda x: retriever.get_relevant_documents(x['question']),
        "question": lambda x: x['question']
    }) | prompt | gemini

    print(f"벡터 디비 불러오기완료 : {vFile}")
    return True

# 로드된 벡터디비에서 정보검색
# 에코서버 : echo server
def chat_query(msg):
    global chain

    response = chain.invoke({'question':msg}).content
    answer = response
    return answer

##################
# 테스트


# vectordb_save('rain2')
# if vectordb_load('rain2') == False:
#     print("벡터DB 불러오기에 실패하였습니다.")
#     exit()

# # # 채팅 시뮬레이션
# while True:
#     msg = input("질문[q:종료]:")
#     if msg in ['q','exit']:
#         print("프로그램종료")
#         exit()
#     answer = chat_query(msg)
#     print(answer)