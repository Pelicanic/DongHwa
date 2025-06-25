<div align="center" >

# Pel-World: AI 인터랙티브 동화 생성 서비스
사용자 맞춤 동화와 삽화, 음성까지 자동 생성하는 웹 기반 인터랙티브 동화 생성 서비스


## 시연 영상

(링크 또는 영상 캡처 이미지 삽입 예정)

</div>



<br>

## 🔖 목차
1. [서비스 소개](#1-서비스-소개)
2. [서비스 제작 기간](#2-서비스-제작-기간)
3. [멤버 및 역할](#3멤버-및-역할)
4. [Tech Stack](#4-tech-stack)
5. [Pipeline](#5-pipeline)
6. [LangGraph 구조](#6-langgraph-구조)
7. [이미지 생성 구조](#7-이미지-생성-구조)
8. [TTS 구조](#8-tts-구조)
9. [데이터 구조](#9-데이터-구조)
10. [예시 결과](#10-예시-결과)
11. [이슈 및 해결](#11-이슈-및-해결)
12. [동작 화면](#12-동작-화면)
13. [느낀점](#13-느낀점)

<br>


## 1. 서비스 소개

Pel-World는 자녀 정보와 입력 값 기반으로 AI가 동화를 생성하고, 문단마다 삽화를 포함하며, 음성(TTS)을 제공하는 인터랙티브 동화 생성 서비스 입니다.  
사용자는 질문-선택지 기반 인터페이스로 동화 흐름을 직접 선택하고 이어갈 수 있습니다.

<br>

## 2. 서비스 제작 기간

- 2025-06-01 ~ 2025-06.23

<br>

## 3.멤버 및 역할

### TEAM Pelicanic 
 >일단 벌리고 보자, 팰리컨처럼.
 
 
![](https://i.imgur.com/bW4l6we.png)


### 멤버 구성

 <img width="100" alt="image" src="https://i.imgur.com/jxAsjiR.png)"> <img width="100" alt="image" src="https://i.imgur.com/wPvrwKM.png"> <img width="100" alt="image" src="https://github.com/user-attachments/assets/af5e73d5-542b-4ed1-a733-97a67b2941c3">

- 김진규 : 프로젝트 기획 / 총괄
- [이석환](https://github.com/seokhwanlee90) : 백엔드 / TTS, CLOVA Voice 연동
- [최재우](https://github.com/cjw2500) : 프론트엔드 / LangChain 삽화 이미지 생성
- [최준혁](https://github.com/kimbap918) : 백엔드 / LangGraph, LLM 설계 및 흐름 제어

<br>

## 4. Tech Stack
- Back End  
    <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=ffffff"/> <img src="https://img.shields.io/badge/Django-092E20?logo=django&style=flat-square"/> <img src="https://img.shields.io/badge/REST framework-009688?style=flat-square&logo=Django&logoColor=ffffff"/> <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&style=flat-square"/>
- Front End  
	<img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=Next.js&logoColor=white"/> <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?logo=tailwindcss&style=flat-square&logoColor=white"/>
- AI/LLM  
	![Google Gemini](https://img.shields.io/badge/-Google_Gemini-4285F4?logo=google&logoColor=white&style=flat-square) <img src="https://img.shields.io/badge/LangChain-000000?logo=langchain&style=flat-square"/> <img src="https://img.shields.io/badge/LangGraph-6366F1?/style=flat-square"/> <img src="https://img.shields.io/badge/Stable Diffusion-FF385C?logo=artstation&style=flat-square"/> 
- Infra & Tools  
	<img src="https://img.shields.io/badge/GitHub-181717?logo=github&style=flat-square"/> <img src="https://img.shields.io/badge/Figma-F24E1E?style=flat-square&logo=Figma&logoColor=ffffff"/> <img src="https://img.shields.io/badge/Clova Voice-03C75A?logo=naver&style=flat-square"/>  


<br>

## 5. Pipeline

- 사용자 입력 → LangGraph 플로우 시작
- story_id 생성 및 요약 흐름(기-승-전-결) 생성
- 문단 생성 → 삽화 필요 시 이미지 생성
- 문단 저장 → Paragraph QA 저장 → 이미지 저장
- 마지막 단락(10단락) 도달 시: 자동 마무리 정리
- 제목, 요약, 완성본 10문단 생성 → PDF 제공

<br>

## 6. LangGraph 구조

![](https://i.imgur.com/RbsU40a.png)


- 상태 기반 흐름(StateGraph) 구성 
- 주요 노드:
    - `GenerateStoryPlan`: 사용자 입력 기반 기승전결 흐름 생성
    - `RetrieveContext`: 이전 문맥 기억, 벡터 DB 또는 DB에서 검색
    - `GenerateParagraph`: 문단 생성 ([문장], [질문], [행동] 포함)
    - `SaveParagraph`, `UpdateParagraphVersion`: 문단 저장 또는 수정
    - `DetectAndUpdateStory`: 등장인물 자동 추출 및 요약 보정
    - `SaveQA`: 문단에 대한 질문-답변 저장
    - `GenerateImage`: 이미지 프롬프트 분석 및 생성
    - `FinalizeStory`: 전체 정리 및 제목/요약/완결 스토리 생성
        
- 분기 조건에 따라 흐름 제어:
    - 문단 수 10개 이상 → FinalizeStory 이동
    - 이미지 필요 여부에 따라 `GenerateImage` 또는 건너뜀
    - `mode=create` vs `edit`에 따라 저장 방식 분리
        
<br>

## 7. 이미지 생성 구조
- 문단 내용 + 캐릭터 정보를 기반으로 삽화 생성
- Gemini를 활용한 프롬프트 통합 분석
- Stable Diffusion 최적화 프롬프트 자동 생성:
    
    - 캐릭터 수, 특징 강조 ((())) 형태 사용
    - 배경, 상황, 등장 사물 강조
    - 스타일: `fairy-tale`, `dreamy`, `children's illustration`, `watercolor`
        
- 결과:
    - `caption_text`, `labels`, `positive_prompt` 생성 후 저장
        
<br>

## 8. TTS 구조
- Google Gemini -> 문장 감성 분석
- 감성 분석된 문단 -> CLOVA Voice 전달
- 각 문단 단위로 음성 변환 가능
- 추후 사용자 맞춤형 TTS (예: 부모 목소리 기반)로 확장 예정
- 완성본 전체 TTS → 동화 오디오북으로 저장 가능

<br>

## 9. 데이터 구조
![](https://i.imgur.com/lGjYJFY.png)

| 테이블명                 | 설명                      |
| -------------------- | ----------------------- |
| **User**             | 사용자 계정 및 프로필 정보         |
| **Story**            | 동화 메타데이터 (작성자 포함)       |
| **StoryParagraph**   | 각 문단의 본문 내용             |
| **ParagraphVersion** | 문단별 버전 관리 (수정 이력 추적)    |
| **Illustration**     | 문단에 연결된 이미지 + 프롬프트 + 캡션 |
| **ParagraphQA**      | 사용자 입력 저장 (질문/선택지/선택결과) |

<br>

## 10. 예시 결과

**입력 예시**: 
* 최초 입력은 아래와 같이 주입됩니다.

"성냥 팔이 소녀" 풍의 동화를 생성해줘, Theme : 고전, Mood : 따뜻한, 주인공의 이름은 "마리", 주인공의 성별은 "여자"

<br>

**출력 예시:**

- 제목: 따뜻한 국밥 한 그릇
- 요약: `추운 겨울 밤, 성냥을 팔던 마리는 배고픔에 국밥집에 들어갔지만 돈이 없었습니다. 국밥집 주인은 딱한 사정을 듣고 따뜻한 국밥을 공짜로 주었고, 마리는 따뜻한 마음으로 다시 힘을 내 성냥을 팔기로 결심합니다.`
- 기승전결: 기, 승, 전, 결을 10개로 나눈 구조로 생성
- 문단 구조: 10개 단락
- 삽화: 각 문단에 따른 맞춤형 이미지 생성
``` text
추운 겨울 밤, 마리는 낡은 갈색 외투를 꼭 여미고 좁은 골목길에 서 있어요. 작은 손에는 성냥 한 묶음이 들려 있답니다. "성냥 사세요~" 하고 작고 떨리는 목소리로 외쳐 보지만, 사람들은 바쁜 걸음으로 마리를 지나쳐 가요. 마리는 집으로 돌아가 따뜻한 저녁을 먹는 사람들을 부러운 눈으로 바라본답니다. 오늘 밤에도 성냥을 다 팔지 못하면 춥고 배고픈 밤을 보내야 해요.
```

<br>

## 11. 이슈 및 해결 

### Backend
| 트러블 요약              | 문제 설명                                      | 해결 방법                                                                  |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------- |
| **1. 상태 전파 누락**     | 요약/캐릭터가 다음 프롬프트에 반영되지 않음 → 문맥 단절           | `passthrough_start()`로 state에 DB값 캐싱, 각 노드에서 일관성 유지                    |
| **2. 문체 붕괴 현상**     | 문단 중간에 '~했다' 체로 전환되어 몰입감 저하                | 프롬프트에 `~해요/어요` 말투 고정 + 과거형 금지 지침 삽입                                    |
| **3. 요약 이탈 문제**     | 사용자 입력이 기존 story_plan을 벗어남 → 흐름 붕괴         | `detect_and_update_story()`로 입력 반영 요약 재작성                              |
| **4. 캐릭터 중복 등장**    | 같은 인물이 이름만 다르게 반복 생성됨 (ex. 루나 vs 루나가, 루나는) | `is_duplicate_character()`로 이름/설정 유사도 검사 → 중복 방지                       |
| **5. 결말 문단 어색함**    | 마지막 문단이 끊긴 느낌, 감정 마무리 부족                   | sub-stage 별 프롬프트 지시 및 instruction_suffix로 paragraph_no 별 점진적 감정 정리 유도 |
| **6. 문맥 무관 질문/선택지** | 문단 내용과 관련 없는 질문이나 뜬금없는 선택지 생성              | `get_substage_instruction()` + Chain of Thought 방식으로 질문 연결성 강화         |
| **7. 등장인물 과잉 생성**   | 불필요한 요정, 동물 등 인물이 무분별하게 생성됨                | 프롬프트에서 “기존 인물 재사용” 우선 유도 + 등장인물 제한 조건 추가                               |
| **8. 과도한 요약 변경**    | 요약 업데이트가 기존 흐름을 전면 뒤엎는 문제 발생               | 요약 변경 범위 제한 지침 추가 + 프롬프트에서 “흐름 유지 우선” 명시                               |

<br>

### Frontend
| 트러블 요약                  | 문제 설명                                                        | 해결 방법                                                                              |
| ----------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **1. Pre-Rendering 이슈** | Next.js의 SSR 특성상 데이터 로딩 전에 HTML이 먼저 렌더링됨 → 빈 값 혹은 오류 발생      | **로딩 컴포넌트 추가** → 모든 데이터 로딩 완료 후 렌더링되도록 처리                                          |
| **2. router.push 이슈**   | `router.push()`는 URL만 바꾸고 컴포넌트를 재실행하지 않음 → `useEffect` 작동 안함 | `window.location.href`로 페이지 이동 → 강제 새로고침 발생 → useEffect 재실행 유도                     |
| **3. Next.js 익숙치 않음**   | 초기 프로젝트에서 Next.js 구조 이해 부족으로 상태 관리, 라우팅, SSR 관련 혼란           | 실제 렌더링 타이밍 흐름 파악 → `useEffect`, `useRouter`, `getServerSideProps` 등의 구조적 이해로 점진 해결 |

<br>


## 12. 동작 화면

1. 메인 페이지
![](https://i.imgur.com/fKhPdV5.png)


<br>

2. 동화 시작
![](https://i.imgur.com/NuOQemY.png)

<br>

3. 동화 생성
![](https://i.imgur.com/2vlc4Yz.png)


<br>


선택지 및 직접 입력으로 이야기 전개가 가능합니다.

![](https://i.imgur.com/6JFOR5E.png)

<br>

4. 동화 완성 
* 동화 생성 기능을 통해 생성한 동화책을 이미지와 TTS, 배경음악과 함께 감상할 수 있습니다.
![](https://i.imgur.com/opLBZsA.jpeg)



<br>

5. 나의 동화책 
* 내가 생성한 동화책을 열람할수 있습니다.
![](https://i.imgur.com/p9R0cVX.jpeg)


<br>
6. 기존 동화책
* 기존의 생성된 동화책을 열람할 수 있습니다.

![](https://i.imgur.com/qrngZkM.jpeg)


<br>


7. 창작 동화책 
* 기존 동화책 이외의 사용자들의 창작 동화책을 감상할 수 있습니다.
![](https://i.imgur.com/NToe22q.png)

<br>

## 13. 느낀점
이 프로젝트를 통해 LLM 기반 서비스 개발의 실제 어려움과 해결과정을 직접 체험했습니다. 초기에 예상치 못한 모델의 행동이나 시스템 통합 이슈로 어려움이 있었지만, 전혀 경험이 없던 LangGraph를 헤쳐나가며 상태 기반 흐름 설계와 분기 처리, 노드 간 데이터 전달, LLM 출력의 통제 방식을 점차 익히게 된 좋은 기회였습니다.

특히 프롬프트 설계에서 느낀점이 많은데, 내가 원하는 출력을 만들기 위해서 'LLM을 설득 시키는' 과정은 너무 과하지도, 너무 느슨하지도 않게하는 완급 조절의 연속이었던 것 같습니다. 그래서 LLM을 위한 메뉴얼을 만들어 주고 약속을 잘 지키는지 생각하게 해주었습니다. 

이 과정에서 알게된건 'LLM은 기억하지 않기 때문에 우리가 기억하게 만들어야 한다' 는 점이었습니다. 상태 관리, 프롬프트는 단순 지시가 아니라, 모델이 올바른 맥락을 ‘착각하게 만드는 기술’이라는 생각으로 다가가게 됐습니다. 
