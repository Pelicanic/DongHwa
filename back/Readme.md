
## 전체 아키텍처 설계

- **프론트엔드**:
  
    - Next.js (React 기반) + Tailwind CSS (or MUI)
    - LangChain과 KoBERT 를 이용해 결과를 사용자에게 보여주는 UI
    
    **백엔드 (API)**:
    
    - Python 3.11 + 기반 Django REST Framework
    - LangChain, KoBERT 분류 모델, 벡터 DB 연동
    - 음성 처리 및 생성형 AI 엔진 포함
    
    **데이터베이스**:
    
    - 유저 정보 및 동화 데이터 → 관계형 DB (예: PostgreSQL, Supabase)
    - LangChain용 벡터 DB (예: Pinecone, Weaviate, Chroma)



<br>




## 폴더/레포 초기 구조
``` ruby
DongHwa/
├── frontend/               # Next.js 프론트엔드 (React 기반)
│   ├── app/                # 페이지 및 라우트 정의 (App Router)
│   │   ├── page.tsx        # 루트 페이지
│   │   ├── about/
│   │   │   └── page.tsx
│   │   └── layout.tsx      # 공통 레이아웃 (헤더/푸터)
│   ├── components/         # 재사용 컴포넌트
│   ├── public/             # 정적 파일 (이미지 등)
│   ├── styles/             # 스타일 (CSS, Tailwind 등)
│   ├── package.json
│   └── next.config.js
├── backend/                # Python 3.11, Django 기반 백엔드
│   ├── manage.py           # Django 관리 스크립트
│   ├── donghwa_project/    # Django 프로젝트 설정 (settings.py 등)
│   └── api/                # 주요 앱 (API, ML 모델, 음성 처리 등)
│       ├── views.py
│       ├── urls.py
│       ├── models.py
│       └── serializers.py  # 필요시 추가
├── data/                   # 데이터 샘플, 학습 데이터, ERD 등
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
[Python 백엔드 (backend/Django REST Framework)]
   - 요청 처리 (ex: LangChain, KoBERT, 음성처리)
   - DB 연동 (PostgreSQL, 벡터 DB 등)
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

<br>

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
conda create -n p311_donghwa python=3.11
conda activate p311_donghwa
```

<br>

2. 라이브러리 설치
* 추후 추가나 삭제 될 수 있음
* **requirements.txt 로 생성해두었습니다.**
* pip install -r requirements.txt 로 설치

``` bash
# ========================================
# requirements.txt (2025년 5월 기준, langgraph 중심 호환)
# Python 3.11 + Gemini 음성 시스템 포함 통합 버전
# ========================================

# === [Django 기반 웹 백엔드] ===
Django~=4.2.13
djangorestframework~=3.15.1
django-cors-headers==4.7.0
gunicorn~=22.0.0
python-dotenv~=1.0.1

# === [데이터베이스 드라이버: MySQL or MariaDB 중 택 1] ===
mysqlclient~=2.2.4
# mariadb~=1.1.9

# === [FastAPI 기반 서비스 지원] ===
fastapi~=0.111.0
uvicorn[standard]~=0.30.1
httpx~=0.27.0

# === [LangGraph + LangChain 0.2.x 호환] ===
langchain~=0.2.17
langchain-core~=0.2.43
langgraph==0.2.1
langchain-google-genai~=1.0.6
google-generativeai~=0.7.1
tiktoken~=0.7.0

# === [WebSocket + Gemini 음성 시스템용] ===
websockets~=12.0

# === [음성 처리 (STT / TTS)] ===
openai-whisper==20231117
gTTS~=2.5.1
soundfile~=0.12.1
ffmpeg-python~=0.2.0
# pyaudio~=0.2.14
# (설치 별도: macOS → brew install portaudio && pip install pyaudio)
# (Windows → pip install pipwin && pipwin install pyaudio)

# === [머신러닝 / KoBERT / 트랜스포머] ===
torch==2.3.1
torchaudio==2.3.1
torchvision==0.18.1
transformers~=4.41.2
sentencepiece~=0.2.0
scikit-learn~=1.5.0
pandas~=2.2.2

# === [벡터 검색 / RAG용] ===
faiss-cpu~=1.7.4

# === [기타 유틸리티] ===
pydantic~=2.7.4
Pillow~=10.3.0
requests~=2.32.3
packaging~=24.1


```


<br>


### 3. Django 프로젝트 및 앱 생성

``` bash
django-admin startproject pelworld .
python manage.py startapp api
```

<br>

### 4. 기본 설정 변경 (`pelworld/settings.py`)

- `INSTALLED_APPS`에 추가

``` python


INSTALLED_APPS = [
    ...,
    'rest_framework',
    'corsheaders',
    'api',  # 우리가 만든 앱
]
```

- CORS 설정 추가 (Next.js 개발 서버 허용)

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...,
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

<br>

### 5. 기본 API 뷰 작성 (`api/views.py`)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello(request):
    return Response({"message": "DongHwa Backend API is running."})
```

<br>

### 6. URL 연결 (`api/urls.py`)

```python
from django.urls import path
from .views import hello

urlpatterns = [
    path('', hello),
]
```

- `backend_project/urls.py`에 포함

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

<br>

### 7. 서버 실행

```bash
python manage.py runserver
```

<br>

------

## 서로의 역할

1. **Django REST Framework (백엔드)**
   - Python 기반 웹 프레임워크 Django 위에서 API 서버 구축
   - LangChain, KoBERT 모델 연동 및 데이터베이스 처리
   - 클라이언트 요청 처리 후 JSON 형태로 응답 전달
2. **Next.js (프론트엔드)**
   - React 기반 UI 개발
   - 사용자 입력 받아 Django API 호출
   - 받은 데이터로 UI 렌더링

두 시스템은 API 요청/응답을 통해 상호작용하며, CORS 설정으로 안전하게 통신합니다.





**추후 공부하는대로 업데이트 할게요!**

