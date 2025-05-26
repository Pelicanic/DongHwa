
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
# --- 웹 프레임워크 ---
Django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.0

# --- 과학/머신러닝 라이브러리 ---
numpy>=1.23.5
torch>=2.0.1
torchvision>=0.15.2
torchaudio>=2.0.2
transformers>=4.31.0
sentence-transformers>=2.2.2

# --- 벡터 DB ---
chromadb>=0.3.21

# --- LangChain 및 OpenAI 연동 ---
langchain>=0.0.303
openai>=0.27.8

# --- 데이터 검증 및 유틸리티 ---
pydantic>=1.10.11   # Django에서는 꼭 필요하진 않음
packaging>=23.1
ydata-profiling>=4.5.1

# --- 이미지 처리 ---
pillow>=9.5.0

# --- TTS/STT 및 음성 처리 ---
pyaudio>=0.2.13
websockets>=11.0
python-dotenv>=1.0.0
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



## Step 3: 백엔드 기초 토대 만들기

<br>

### 1. backend 폴더 생성 및 환경 세팅

```
bash


복사편집
# DongHwa 레포 루트에서
cd DongHwa
mkdir backend
cd backend

# conda 환경 생성 및 활성화 (Python 3.11)
conda create -n donghwa_env python=3.11 -y
conda activate donghwa_env
```

<br>

### 2. 라이브러리 설치

- 추후 추가 및 변경 가능
- `requirements.txt`로 관리 권장

```
bash


복사편집
pip install django djangorestframework django-cors-headers
pip install numpy torch torchvision torchaudio transformers sentence-transformers
pip install chromadb langchain openai
pip install pillow
```

*`requirements.txt` 예시:*

```
txt


복사편집
Django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.0

numpy>=1.23.5
torch>=2.0.1
torchvision>=0.15.2
torchaudio>=2.0.2
transformers>=4.31.0
sentence-transformers>=2.2.2

chromadb>=0.3.21
langchain>=0.0.303
openai>=0.27.8

pillow>=9.5.0
```

<br>

### 3. Django 프로젝트 및 앱 생성

```
bash


복사편집
django-admin startproject backend_project .
python manage.py startapp api
```

<br>

### 4. 기본 설정 변경 (`backend_project/settings.py`)

- `INSTALLED_APPS`에 추가

```
python


복사편집
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'corsheaders',
    'api',  # 우리가 만든 앱
]
```

- CORS 설정 추가 (Next.js 개발 서버 허용)

```
python


복사편집
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

```
python


복사편집
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello(request):
    return Response({"message": "DongHwa Backend API is running."})
```

<br>

### 6. URL 연결 (`api/urls.py`)

```
python


복사편집
from django.urls import path
from .views import hello

urlpatterns = [
    path('', hello),
]
```

- `backend_project/urls.py`에 포함

```
python


복사편집
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

<br>

### 7. 서버 실행

```
bash


복사편집
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

