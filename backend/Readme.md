
## 전체 아키텍처 설계

- **프론트엔드**:
    - Next.js (React 기반) + Tailwind CSS (or MUI)
    - LangChain과 KoBERT 결과를 보여주는 UI
- **백엔드 (API)**:
    - FastAPI or Flask (Python 기반)
    - LangChain, KoBERT 분류 모델, 벡터 DB 연동   
- **데이터베이스**:
    - 유저 정보/동화 데이터 → RDB (예: PostgreSQL, Supabase)    
    - LangChain용 벡터 DB (예: Pinecone, Weaviate, Chroma)


## 폴더/레포 초기 구조
``` ruby
DongHwa/
├── frontend/               # Next.js App Router 기반 프론트엔드
│   ├── app/                # App Router: 페이지/라우트 정의
│   │   ├── page.tsx        # 루트(/) 페이지
│   │   ├── about/          # /about 페이지
│   │   │   └── page.tsx
│   │   └── layout.tsx      # 공통 레이아웃 (헤더/푸터)
│   ├── components/         # 재사용 컴포넌트 (Button, Header 등)
│   ├── public/             # 정적 파일 (이미지 등)
│   ├── styles/             # CSS/SCSS 모듈 혹은 Tailwind 적용
│   ├── package.json
│   └── next.config.js
├── backend/                # Python 백엔드 (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── ml_model.py
│   │   ├── langchain_flow.py
│   │   └── db.py
│   └── requirements.txt
├── data/                   # 데이터 샘플, ERD, 학습 데이터
├── docs/                   # 문서 (회의록, 설계서 등)
├── README.md
└── .gitignore

```


<br>

## 구조 개념

``` markdown
[사용자]
   |
   ▼
[Next.js 프론트엔드 (frontend)]
   - 사용자 입력 (폼, 버튼 등)
   - fetch/axios로 API 요청
   - 결과 받아서 UI에 출력
   |
   ▼
[Python 백엔드 (backend/FastAPI)]
   - 요청 처리 (ex: LangChain, KoBERT)
   - DB 연동 (PostgreSQL, 벡터DB 등)
   - 응답 반환 (JSON, 이미지 등)
   |
   ▼
[Next.js로 결과 전달]
```


<br>

## Step 1: Next.js 기초 개념 잡기

### Next.js란?
- **React 기반 프레임워크**
- **서버 사이드 렌더링 (SSR), 정적 사이트 생성 (SSG)** 지원
- **라우팅, 코드 스플리팅, API 라우트 등** 기본 제공
- **풀스택 개발까지 가능 (백엔드 + 프론트)**
    

### React와 차이점?

- React는 **라이브러리**라서 단독으로는 라우팅, SSR 등을 직접 구현 해야함.
- Next.js는 **React + 여러 편의 기능**을 제공하는 **프레임워크**.


## Step 2: Next.js 프로젝트 만들기

1️. **Node.js 설치**  
👉 [공식 사이트](https://nodejs.org)에서 최신 LTS 버전 설치

<br>

2️.  **Next.js 프로젝트 생성**

``` bash
npx create-next-app <프로젝트 명>
cd <프로젝트 명> 
npm install
npm run dev
```

<br>

3. app/page.tsx 수정
* app/page.tsx는 루트경로(/) 페이지를 의미함
* 브라우저에서 `http://localhost:3000` 에 접속했을 때 보여주는 메인 홈페이지
``` tsx
// app/page.tsx
export default function Home() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>DongHwa 서비스에 오신 것을 환영합니다!</h1>
      <p>AI를 활용한 동화 생성 및 TTS 기능을 제공합니다.</p>
    </main>
  );
}
```


<br>

4. 실행
``` bash
npm run dev

http://localhost:3000
```

<br>

## Step 3: 백엔드 기초 토대 만들기

<br>
1. backend 폴더 생성 및 환경 세팅
```bash
# DongHwa 레포 루트에서
cd DongHwa
mkdir backend
cd backend

# conda 환경 생성 및 활성화
conda create -n p39_donghwa python=3.9
conda activate p39_donghwa



```

<br>

#### 왜 Python 3.9를 고려하는지?

- **KoBERT 및 LangChain, Transformers 라이브러리의 호환성**:  
    일부 라이브러리(특히 KoBERT 관련)는 최신 Python(3.11, 3.12)에서 아직 완벽히 안정적이지 않을 수있음
- **FastAPI, Pydantic, Hugging Face Transformers 등 주요 라이브러리**는 Python 3.9에서 안정적으로 작동

<br>
2. 라이브러리 설치
* 추후 추가나 삭제 될 수 있음
* **requirements.txt 로 생성해두었습니다.**
* pip install -r requirements.txt 로 설치 
``` bash
# --- 과학/머신러닝 라이브러리 ---
numpy==1.23.5
torch==2.0.1
torchvision==0.15.2
torchaudio==2.0.2
transformers==4.31.0          # NLP 모델 라이브러리
sentence-transformers==2.2.2  # 문장 임베딩 지원

# --- 벡터 DB ---
chromadb==0.3.21               # 벡터 데이터베이스

# --- LangChain 및 OpenAI 연동 ---
langchain==0.0.303             # LangChain 코어 (0.3.61 이상 권장)
openai==0.27.8                 # OpenAI API 연동

# --- 웹 프레임워크 및 서버 ---
fastapi==0.95.2
uvicorn==0.22.0
python-multipart==0.0.6        # 파일 업로드 지원
aiofiles==23.1.0               # 비동기 파일 처리

# --- 데이터 검증 및 유틸리티 ---
pydantic==1.10.11              # 데이터 검증 및 모델링 (2.x 최신 버전 고려 가능)
packaging==23.1                # 패키지 관리 (24.x 최신 버전 권장)
ydata-profiling==4.5.1         # 데이터 프로파일링 도구

# --- 이미지 처리 ---
pillow==9.5.0                  # 이미지 처리 라이브러리


# TTS, STT 테스트용 (필요시 추가)
# google-cloud-texttospeech, clova-sdk, whisper 설치는 별도 고려

# (필요하다면 추가) LangGraph 연동 라이브러리 등은 별도 명시

```


<br>

3. backend/app/main.py 생성 후 FastAPI 기본 코드 작성
``` python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI(title="DongHwa Backend API")

# CORS 설정 (Next.js 프론트엔드와 통신을 위한 설정)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"], # Next.js 개발 서버 주소
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],

)
@app.get("/")
```


<br>

4. 실행
``` bash
python -m uvicorn app.main:app --reload
```


<br>

#### 서로의 기능
1. **FastAPI**:
    - Python 기반 백엔드 프레임워크
    - API 서버를 구축하는 데 사용
    - Python 코드로 작성된 서버 로직을 실행
    - 주로 데이터 처리, API 엔드포인트 제공, 데이터베이스 연동 등의 역할을 수행
2. **Next.js**:
    - JavaScript/TypeScript 기반 프론트엔드 프레임워크
    - React 기반으로 웹 애플리케이션을 개발
    - 클라이언트 사이드 렌더링(CSR)과 서버 사이드 렌더링(SSR)을 지원
    - 사용자 인터페이스를 구축하는 데 사용

두 프레임워크는 서로 다른 역할을 수행하며, 일반적으로 다음과 같이 통신합니다.
- Next.js 프론트엔드는 FastAPI 백엔드의 API 엔드포인트를 호출하여 데이터를 요청하고 응답을 받음
- CORS 설정을 통해 두 서버가 서로 통신할 수 있도록 허용


<br>


**추후 공부하는대로 업데이트 할게요!**

