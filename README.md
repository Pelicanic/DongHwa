## 📑 목차

1. [Code Convention 개요 및 목적](#code-convention-%EA%B0%9C%EC%9A%94-%EB%B0%8F-%EB%AA%A9%EC%A0%81)

2. [공통 규칙 (Python & JavaScript)](#%EA%B3%B5%ED%86%B5-%EA%B7%9C%EC%B9%99-python--javascript)
    
3. [🔙 백엔드 (Django, Python)](#-%EB%B0%B1%EC%97%94%EB%93%9C-django-python)
    
4. [💻 프론트엔드 (Next.js, TypeScript)](#-%ED%94%84%EB%A1%A0%ED%8A%B8%EC%97%94%EB%93%9C-nextjs-typescript)
    
5. [Git 사용 규칙 (Git Rule)](#git-%EC%82%AC%EC%9A%A9-%EA%B7%9C%EC%B9%99-git-rule)
    
    - [1. 브랜치 전략](#1-%EB%B8%8C%EB%9E%9C%EC%B9%98-%EC%A0%84%EB%9E%B5)
        
    - [2. 커밋 메시지 규칙](#2-%EC%BB%A4%EB%B0%8B-%EB%A9%94%EC%8B%9C%EC%A7%80-%EA%B7%9C%EC%B9%99)
        
    - [3. Pull Request (PR) 규칙](#3-pull-request-pr-%EA%B7%9C%EC%B9%99)
        
    - [4. 커밋 단위 규칙](#4-%EC%BB%A4%EB%B0%8B-%EB%8B%A8%EC%9C%84-%EA%B7%9C%EC%B9%99)
        
6. [GIT 협업 절차 (CLI 기준)](#git-%ED%98%91%EC%97%85-%EC%A0%88%EC%B0%A8-cli-%EA%B8%B0%EC%A4%80)
    
    - [1. Git Clone](#1-git-clone)
        
    - [2. 브랜치 사용하기](#2-%EB%B8%8C%EB%9E%9C%EC%B9%98-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0)
        
    - [3. Pull Request(PR)](#3-pull-requestpr)
        
    - [4. 원격 ↔ 로컬 동기화](#4-%EC%9B%90%EA%B2%A9--%EB%A1%9C%EC%BB%AC-%EB%8F%99%EA%B8%B0%ED%99%94)
        
    - [5. 로컬 브랜치 정리](#5-%EB%A1%9C%EC%BB%AC-%EB%B8%8C%EB%9E%9C%EC%B9%98-%EC%A0%95%EB%A6%AC)
        
7. [추천 GUI 툴](#%EC%B6%94%EC%B2%9C-gui-%ED%88%B4)


---


## Code Convention
**Code Convention**은 팀 내에서 **코드를 일관되고 깔끔하게 작성하기 위한 규칙과 스타일 가이드**를 말합니다.  
목표는 다음과 같습니다:

### 🎯 목적
- 팀원 간 **코드 가독성 향상**
- **유지보수**와 **협업**이 쉬운 코드 작성
- **버그 감소** 및 코드 리뷰 효율화
- 개발자 간 **스타일 통일** (개인 습관 최소화)
<br>

## 공통 (Python & JavaScript)

| 항목    | 규칙 예시                                                          |
| ----- | -------------------------------------------------------------- |
| 변수/함수 | `snake_case` (Python), `camelCase` (JS/TS)                     |
| 클래스명  | `PascalCase`                                                   |
| 파일명   | 기능 + 역할명, 모두 소문자 + 언더스코어 (`story_service.py`, `storyCard.tsx`) |
| 주석    | 핵심만 간결하게 (`# 이유`, `// 목적`)                                     |
| 들여쓰기  | 4칸 (Python), 2칸 (JS/TS)                                        |
| 라인 길이 | 100자 이하 권장                                                     |
| 환경변수  | `.env` 파일 사용, Git에 커밋 금지 (`.gitignore`에 명시)                    |
| 함수 분리 | 로직이 길면 `services/` 또는 `lib/`로 분리                               |

---

<br>

## 🔙 백엔드 (Django, Python 3.11)
``` bash
back/
├── api/                # 앱 로직 (views, models, services)
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   ├── serializers.py
│   └── services/
├── pelworld/           # 설정 (settings.py 등)
└── manage.py
```

| 항목       | 규칙                                       |
| -------- | ---------------------------------------- |
| View 클래스 | `APIView`, `GenericAPIView` 기반 사용        |
| 모델 클래스   | `PascalCase`, 컬럼명은 `snake_case`          |
| 시리얼라이저   | 필드 명시, `Meta` 정의 필수                      |
| 라우팅      | `urls.py`에서 앱 단위로 명확히 분리                 |
| 서비스 분리   | 복잡한 비즈니스 로직은 `services/` 하위로 분리          |
| 응답 구조    | `{ success, message, data }` JSON 형태로 통일 |
| 예외 처리    | `try-except`, `ValidationError` 적절히 사용   |

### 예시(Django)
``` python
# story_service.py
# 작성자: 홍길동
# 기능: 사용자 동화 추천 기능 로직 정의
# 마지막 수정일: 2025-06-01

from django.http import JsonResponse
from .models import Story, UserGenre

def recommend_stories(user_id):
    try:
        # 사용자의 선호 장르 조회
        genre_ids = UserGenre.objects.filter(user_id=user_id).values_list("genre_id", flat=True)
        if not genre_ids:
            return JsonResponse({"message": "선호 장르 없음"}, status=404)

        # 장르 기반 추천 동화 10개 반환
        stories = Story.objects.filter(genres__genre_id__in=genre_ids).distinct()[:10]
        return JsonResponse({"results": list(stories.values())})

    except Exception as e:
        # 예외 처리: 서버 내부 오류 응답
        return JsonResponse({"error": f"오류 발생: {str(e)}"}, status=500)

```

<br>

---



## 💻 프론트엔드 (Next.js, TypeScript)
```bash
front/
├── app/              # 라우트 기반 폴더 구조
├── components/       # 재사용 UI 컴포넌트
├── styles/           # Tailwind 및 글로벌 스타일
├── lib/              # API 함수, 유틸 등
├── public/           # 정적 파일

```

| 항목     | 규칙                                          |
| ------ | ------------------------------------------- |
| 파일 구조  | `page.tsx`, `layout.tsx` 등 App Router 구조 활용 |
| 컴포넌트 명 | `PascalCase`, props는 타입 명시                  |
| API 함수 | `lib/` 디렉토리에 분리                             |
| CSS    | Tailwind 유틸 클래스 사용                          |
| 상태 관리  | 기본은 useState, 필요시 Context 또는 Zustand 등      |
| 폴더명    | 라우트 기준 명확하게 구성 (`/story`, `/about` 등)       |

<br>

### TypeScript 예시 (Next.js)
``` python
/**
 * StoryCard.tsx
 * 작성자: 김개발
 * 설명: 동화 정보를 카드 형태로 렌더링
 * 작성일: 2025-06-01
 */

import React from 'react'

type Props = {
  title: string
  summary: string
}

const StoryCard = ({ title, summary }: Props) => {
  // 카드 UI 출력
  return (
    <div className="rounded-lg shadow-md p-4">
      <h3 className="text-lg font-bold">{title}</h3>
      <p className="text-sm text-gray-700">{summary}</p>
    </div>
  )
}

export default StoryCard



```


<br>

---


## Git 사용 규칙 (Git Rule)
**Git Rule**은 Git을 사용하는 팀원들이 **일정한 방식으로 브랜치를 만들고, 커밋하고, PR(풀 리퀘스트)**을 보내는 등  
**형식과 절차를 통일하기 위한 협업 규칙**입니다.


## 🎯 Git Rule의 목적

- 협업 중 **충돌 최소화**
- 작업 흐름을 **명확히 공유** 
- 커밋 메시지와 브랜치를 **이해하기 쉽게 정리**
- 리뷰, 롤백, 히스토리 추적이 쉬워짐


<br>

## 1. 브랜치 전략

### 기본 브랜치

- `main` : **프로덕션(배포)** 용 브랜치

<br>

### 기능 브랜치
- `feature/` : 기능 개발 (예: `feature/signup-api`)
- `fix/` : 버그 수정 (예: `fix/login-error`)
- `test/` : 테스트 코드 작성
- `docs/` : 문서 작성 또는 수정 (예: README, API 명세 등)
- `ml/` : 머신러닝 관련 코드 (예: `ml/recommender-koBERT`)
    

### 예시
|용도|형식 예시|
|---|---|
|기능 개발|`feature/login-page`|
|버그 수정|`fix/image-upload-error`|
|문서 작업|`docs/readme-update`|
|테스트|`test/story-generation`|
|리팩터링|`refactor/api-cleanup`|



---

## 2. 커밋 메시지 규칙

#### 커밋 타입(prefix)

| 타입         | 설명                      |
| ---------- | ----------------------- |
| `feat`     | 새로운 기능 추가               |
| `fix`      | 버그 수정                   |
| `docs`     | 문서 수정 (README 등)        |
| `style`    | 코드 스타일 (공백, 들여쓰기 등) 변경  |
| `test`     | 테스트 코드 추가 또는 수정         |
| `chore`    | 빌드 설정, 패키지, config 등 기타 |

#### 커밋 메시지 형식
```bash
<타입>: [기능 요약] - (선택) 상세 설명

git commit -m "feat: 동화 생성 기능 추가"
git commit -m "fix: 문단 버전 오류 수정"
```


<br>

### 3. Pull Request (PR) 규칙

- PR 제목: `[타입] 설명 (영문 또는 국문)`
    - 예: `[feat] 사용자 추천 API 구현`      
- PR 본문: 변경 내용 요약 + 작업 이유 + 관련 이슈 태그
- 리뷰어 지정 필수
- Merge는 코드 리뷰 후 진행이 원칙


<br>

### 4. 커밋 단위 규칙
- 너무 자주 X, 너무 몰아서도 X
- **한 커밋 = 하나의 의미 있는 작업**
    - ❌ `"fix: 여러 가지 수정"`
    - ✅ `"fix: 문단 삽화 API 응답 오류 수정"`


<br>

``` bash
# 브랜치 생성
git checkout -b feature/story-recommendation

# 커밋
git add .
git commit -m "feat: 장르 기반 동화 추천 기능 구현"

# PR 생성
# 제목: [feat] 장르 기반 동화 추천 기능 구현
# 내용: 추천 알고리즘 및 Like 테이블 활용 

```


<br>

---

## GIT으로 협업하기


<br>


1. **GitBash가 설치되어 있다는 가정하에 설명입니다.**
2. **해당 설명은 CLI로 작업하는 방법입니다.**
3. 맨 아래에 GUI툴 추천이 있습니다. CLI에 익숙해지면 GUI를 사용하는것도 쉽게 이해할수 있습니다!

  
  

<br>


## 1. Git Clone : 처음 프로젝트 파일을 받을때 최초 1회만

  

<br>

  

1. Copy url to clipboard를 클릭합니다.

![](https://i.imgur.com/qiwRK1p.png)

  

<br>

  

2. Terminal(Git Bash)를 실행시켜 원하는 경로로 이동합니다.

![](https://i.imgur.com/Ovhcr6v.png)

  
  

<br>

  
  

3. git clone <저장소 주소>를 입력하면 해당 경로에 git 폴더(DongHwa)가 생성됩니다.

![](https://i.imgur.com/GFwb0cC.png)

  

<br>

  

## 2. Branch 사용하기 : 매번 새 작업시마다

- 작업을 할 때 각자의 작업을 식별하고, 작업의 충돌을 방지하기 위해 branch를 사용합니다.

  

<br>

  

**프로젝트 작업은 생성된 DongHwa 폴더에서 진행합니다**

![](https://i.imgur.com/1F5qXe0.png)

1. **git checkout -b 브랜치명** : 새 작업 시작시 git bash에서 브랜치를 생성합니다.

* 브랜치명은 팀에서 정한 git rule에 따르지만, 예시에서는 편하게 각자의 이름으로 합니다.

``` bash

# 예시

git checkout -b choi

# choi라는 브랜치를 생성하고 해당 브랜치로 이동했습니다.

```

![](https://i.imgur.com/BABU2OA.png)

  

<br>

  

예시로, DongHwa 폴더에 준혁 폴더를 만들고 그 안에 test.py라는 작업물을 완성해 넣었습니다.

![](https://i.imgur.com/Qi9wKdk.png)

  
  

<br>

  

2. **git add** : 작업한 내용을 branch의 stage에 추가합니다.

```shell

git add . # 브랜치에 변경된 작업 전부를 추가합니다.

```

  

- 작업물이 추가된 후에는 git status를 통해 어떤 부분이 변경되고 추가 되었는지 확인해보는게 좋습니다.

```bash

git status

```

  

branch 'choi'에서, 새 파일 test.py가 추가된것을 확인했습니다.

![](https://i.imgur.com/vKxL6bq.png)

<br>

  

3. **git commit -m "커밋내용"** : stage에 추가된 작업물을 commit합니다.

``` bash

# 예시

# 커밋내용은 작업한 내용을 자유롭게 쓰면 됩니다.

git commit -m "choi/test.py 작업 완료"

```

커밋이 완료되었습니다.

![](https://i.imgur.com/rswz6Mn.png)

<br>

  

4. **git push origin <브랜치명>** : 브랜치에 commit 된 작업을 push합니다.

* 푸시는 꼭 자기 브랜치에!

* **main에 바로 푸시하면 안됩니다.**

```bash

# 예시

git push origin choi

```

성공적으로 업로드 되었습니다. 하지만 여기서 끝이 아닙니다!

![](https://i.imgur.com/Jy7xDVW.png)

  
  

<br>

  
  

## 3. Pull Request(PR) : Branch에서 작업한 것을 Main에 통합하는 과정

  

1. DongHwa로 가면 Compare & Pull request가 뜬걸 볼수있습니다. 클릭해줍시다.

![](https://i.imgur.com/kEYgV0b.png)

  

<br>

  

2. 충돌이 없다면 Able to merge가 떠있는것을 확인할 수 있습니다. 문제가 없다면 Create pull request를 누릅니다.

* compare가 자신의 브랜치가 맞는지

* base가 main이 맞는지 확인해주세요

* description은 필수는 아니지만 작업을 하며 바뀐것에 대해 설명을 해주시는것이 좋습니다.

![](https://i.imgur.com/yEBkIGO.png)

  
  

<br>

  

3. Merge pull request로 Main과 병합합니다.

* 이 과정에서 Merge pull request를 누르는건 보통 팀장이 코드를 검토 후에 시행합니다.

* 일단 눌러줍시다

  

![](https://i.imgur.com/aXiEfSA.png)

  

<br>

  

4. 다음 작업의 혼선을 방지하기 위해 작업이 완료된 원격 브랜치를 삭제합니다.

![](https://i.imgur.com/3Kj9obd.png)

  

<br>

  
  

## 4. 원격 저장소의 변동 내역을 로컬 저장소(내 컴퓨터)와 연동하기

* 작업 후 원격 저장소(github 저장소)에 변경된 내역들을 로컬 저장소(내 컴퓨터)에도 반영해야합니다.

* 이 과정에서 여러 사람들과의 협업에도 작업들을 손쉽게 가져올 수 있는 git의 장점이 드러납니다.

  
  

1. **git checkout main** : 브랜치에서 메인으로 돌아갑니다.

![](https://i.imgur.com/MIpeiNr.png)

  
  

<br>

  

2. **git pull origin main** : 원격 저장소의 main에서 변경된 사항을 로컬 저장소에 반영합니다.

* 이제 원격 저장소와 내 로컬 저장소의 모든 사항이 동기화 됐습니다.

![](https://i.imgur.com/qXWqkWR.png)

  

<br>

  

3. **git branch -d <브랜치명>**

* 원격과 로컬 모든 사항이 동기화 됐으니, 혼선을 방지하기 위해 사용한 로컬의 브랜치 또한 삭제합니다.

* 여기까지가 Github에서 작업 생성, 업로드, 동기화의 모든 과정입니다.

* 다시 **새 작업을 시작할때 git checkout -b 브랜치명으로 브랜치를 생성하고 같은 과정을 반복합니다.**

``` bash

# 예시

# -d는 삭제 입니다.

git branch -d choi

```

![](https://i.imgur.com/P4JyxaP.png)

  
  
  

<br>

  
  
  

## 5. GUI Tools

CLI 보단 GUI 방식으로 작업하는게 직관적이고 충돌을 관리하기에 용이합니다.

  

SourceTree Mac 및 Windows 용으로 사용할 수 있는 무료 git GUI tool 사용하기 쉽고 직관적인 UI로 git 브랜치, 태그, 커밋, 병합 등을 관리할 수 있습니다. 일반적인 git 작업뿐만 아니라, Git-flow 작업도 지원합니다.

  

맥OS 및 윈도우용 다운로드 링크: https://www.sourcetreeapp.com/

  

GitHub Desktop 맥OS 및 윈도우용으로 사용할 수 있는 git GUI tool git 커밋, 브랜치, 병합 등의 작업을 직관적인 UI로 관리할 수 있습니다. GitHub 계정과 연동하여, 원격 저장소를 쉽게 관리할 수 있습니다.

  

맥OS 및 윈도우용 다운로드 링크: https://desktop.github.com/

  

Fork Mac 및 Windows 용으로 사용할 수 있는 git GUI tool 강력한 UI와 기능으로 git 작업을 보다 쉽고 빠르게 수행할 수 있습니다. Git-flow를 지원하며, 코드 검토 및 충돌 해결 기능도 제공합니다.

  

맥OS 및 윈도우용 다운로드 링크: https://git-fork.com/

  

Git GUI Mac, Windows, Linux 용으로 사용할 수 있는 무료 git GUI tool git 작업을 쉽게 수행할 수 있는 UI를 제공합니다. 다양한 git 명령어를 지원하며, 코드 검토 및 충돌 해결 기능도 제공합니다.

  

맥OS, 윈도우 및 리눅스용 다운로드 링크: https://git-scm.com/downloads/guis