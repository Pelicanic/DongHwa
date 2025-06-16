# 작성자 : 최재우
# 작성일 : 2025-06-12
import json

from api.models import Storyparagraph,Story
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence  # 중요


debug = True

# ------------------------------------------------------------------------------------------
# 통합 이미지 프롬프트 생성 (성능 최적화: 2회 API 호출 → 1회 API 호출)
# ------------------------------------------------------------------------------------------

# 작성자: 최재우(성능 최적화)
# 기능: 기존 2단계 프롬프트(analysis + image)를 1단계로 통합하여 API 호출 절반 축소
# 마지막 수정일: 2025-06-16
def generate_image_unified(story_id, paragraph_id, data, check) -> dict:
    """
    이미지 생성 통합 함수 (성능 최적화)
    기존 2단계 프롬프트를 1단계로 통합하여 API 호출 절반 축소
    
    Args:
        story_id: 스토리 ID
        paragraph_id: 문단 ID  
        data: 캐릭터 데이터
        check: 'illustration' 또는 'cover_illustration'
        
    Returns:
        dict: {
            "caption_text": str,
            "labels": list,
            "positive_prompt": str
        }
    """
    # DB에서 데이터 가져오기
    story = Story.objects.get(story_id=story_id)
    story_paragraph = Storyparagraph.objects.get(paragraph_id=paragraph_id)
    
    # 기본 캐릭터 데이터 설정
    if not data:
        data = " 1. 메리(주인공): 여자, 갈색 털, 8세, 토끼 2. 알렉스: 남자, 붉은 털, 9세, 다람쥐 3. 올빼미: 남자, 하얖색 깃털, 10세, 부엉이 4. 거미 괴물: 성별 불명, 검은색 털, 나이 불명, 거미 괴물"
    
    # 컨텐츠 선택
    content = story_paragraph.content_text if check == "illustration" else story.summary
    
    # 통합 프롬프트 (분석 + 이미지 생성을 한 번에 처리)
    unified_prompt = f"""
    당신은 동화책 이미지 생성을 위한 Stable Diffusion 프롬프트 전문가입니다.
    주어진 텍스트를 분석하여 즉시 Stable Diffusion용 이미지 프롬프트와 메타데이터를 생성해주세요.
    
    **분석해야 할 텍스트:**
    {content}
    
    **캐릭터 정보:**
    {data}
    
    **프롬프트 생성 규칙:**
    1. 강조는 ((( )))로 작성
    2. 주인공은 반드시 포함
    3. 등장인물 수는 텍스트에서 나오는 인원수와 동일하게 작성
    4. 등장인물의 특징은 "캐릭터 정보"의 같은 이름이 가진 특징을 기준으로 강조하여 작성
    5. 동화풍으로 나올 수 있도록 프롬프트 작성
    6. 등장인물이 남자면 "BOY", 여자면 "GIRL"로 프롬프트 작성
    7. 상황과 배경, 사물을 강조하여 프롬프트 작성
    8. 주인공은 얼굴이 보이게 프롬프트 작성
    9. 장면이 한 장면만 나오도록 프롬프트 작성
    10. 모든 프롬프트는 Stable Diffusion에 최적화된 영어로 작성
    
    **기본 품질 태그 포함:**
    {POSITIVE_PROMPT_BASE}
    
    **출력 형식 (JSON):**
    반드시 다음 형식으로 응답해주세요:
    {{
        "caption_text": "한글로 작성된 장면 설명",
        "labels": ["라벨 1", "라벨 2"],
        "point": "등장인물의 이름, 성별, 종족, 사물",
        "positive_prompt": "Stable Diffusion용 긴정 프롬프트"
    }}
    
    **주의사항:**
    - 분석 과정은 생략하고 최종 결과만 출력하세요
    - JSON 형식을 엄격히 준수하세요
    - 한글과 영어를 적절히 혼용하세요
    """
    
    try:
        # 단일 API 호출로 통합 처리
        response = model.invoke(unified_prompt)
        content = response.content
        
        if debug:
            print(f"[UnifiedImageGeneration] 통합 응답: {content}")
        
        # JSON 추출 및 파싱
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
        else:
            json_content = content
            
        result = json.loads(json_content)
        
        if debug:
            print(f"[UnifiedImageGeneration] 파싱 결과: {result}")
            
        return result
        
    except Exception as e:
        if debug:
            print(f"[UnifiedImageGeneration] 오류: {e}")
        # 기본값 반환
        return {
            "caption_text": "동화 장면",
            "labels": ["장면", "배경"],
            "positive_prompt": f"{POSITIVE_PROMPT_BASE}, digital art, detailed, high quality"
        }


# ------------------------------------------------------------------------------------------
# Gemini 초기화 및 모델 정의
# ------------------------------------------------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    streaming=False
)


# ------------------------------------------------------------------------------------------
# 긍정, 부정 프롬프트 정의
# ------------------------------------------------------------------------------------------
POSITIVE_PROMPT_BASE = "((masterpiece)), ((best quality)), ((detailed)), ((highly detailed)), ((cinematic lighting)), 4K, fairy-tale, children's illustration, style of children's book, dreamy, fantasy, poetry, nostalgic, water color"
NEGATIVE_PROMPT_BASE = "((half animal)), (( animal hybrid)), animal transformation, were-, lycanthrope, centaur, satyr, minotaur, extra ears, double ears, four ears, multiple ears, artificial, bad quality, bad perspective, bad geometry, worst depth, bad depth, bad dynamics, generic, fused, jpeg artifacts, (missing fingers:1.2), (multiple_views:1.4), downscaled, shortstack, short_stack, loli, child, teen, oldest, lolita, unfinished, duplicated, (extra fingers:1.2), extra digits, artist_name, patreon_logo, signature, watermark, twitter_logo, twitter_name, (long-legs:1.3), (short-torso:1.1), sound_effects, speech_bubble, mosaic_censoring, censoredartificial, censored, (duplicated navel:1.4), ugly, deformed, noisy, low poly, blurry, worst quality, multiple angle, split view, ((looking at viewer)), bad fingers, blue_archive, halo, backlighting, bad lighting, poorly drawn teeth, poorly drawn mouth, close up, (extreme close up), upscaled, fused details, portrait, ai generated, ai assisted, perfect lines, low quality, negative_hand, bad-hands-4, x-ray, futanari, monochrome, greyscale, cross, sepia, lineart, outlines, painting, drawing, illustration, blurry face, clipping, ugly face, glowing hands, extra arms, muscular, deformed body, patreon username, 3d, choker, artist name, capelet, simple background, deformities, b&w, bad hands, poorly drawn hands, too many fingers, too few fingers, badly drawn fingers, bad feet, deformed feet, bad toes, deformed toes, too many toes, too few toes, more than 5 toes, less than 5 toes, excessive number of toes, feet on wrong leg, feet facing wrong direction, backwards feet, too many feet, text, numbers, heart, patreon, twitter, subscribestar, roads, worst detail, sketch, censor, animal, too many, monster, thick, anthro, furry, speech bubbles, writing, dickgirl, (fewer digits:1.3), (duplicated navel:1.1), selfie, see-through_clothes, wet, oily, shiny_skin, painted, clothed animal, side view, realistic, creature, lowres, artistic error, multiple views, displeasing, worst aesthetic, old, early, (multiple girls, multiple boys):1.7, (solo, threesome, three people:1.3), penis lettering, text bubbles, see-through, xray, bad anatomy, duplicate, twin, mirroring, (easynegative, lazyneg, safe_neg, ng_deepnegative_v1_75t), longbody, pubic hair, cropped, extra digit, fewer digits, missing fingers, username, logo, sign, extra limbs, bad art, fused hands, bad proportions, broken finger, distorted hands, compression artifacts, flowers, roses, crown, diadem, masculine, (solo:1.3), (worst quality:2), (low quality:2), out of focus, deformed eyes, bad composition, cartoon style, missing details, poor lighting, flat shading, cluttered background, poor texture, inconsistent style, simple serpent, oversaturated colors, SmoothNoob_Negative, SmoothNegative_Hands-neg, abstract, surreal, messy, (bad eyes), (cross-eyed), (fused eyes), (asymmetrical eyes), (wrong eye direction), (lazy eye), (blurry eyes), (bad nose), (deformed nose), (flat nose), (asymmetrical nose), (bad mouth), (deformed mouth), (fused lips), (missing mouth), (asymmetrical mouth), distorted, nsfw, nude, naked, sex, sexual, panties, nipples, areola, cleavage, breast, pussy, thong, lingerie, erotic, porn, lewd, suggestive, uncensored, exposed, crotch, underboob, undergarments, transparent clothing "

# ------------------------------------------------------------------------------------------
# 패러그래프 생성 관련 (레거시 - 호환성용)
# ------------------------------------------------------------------------------------------

# 레거시 경고: 이 함수는 성능상 이유로 비추천
# 대신 generate_image_unified() 사용 권장

def generate_image_LC(story_id, paragraph_id, data, check) -> dict:
    global POSITIVE_PROMPT_BASE

    # ------------------------------------------------------------------------------------------
    # DB에서 story와 story_paragraph 정보 가져오기
    # ------------------------------------------------------------------------------------------
    story = Story.objects.get(story_id=story_id)
    story_paragraph = Storyparagraph.objects.get(paragraph_id=paragraph_id)

    # ------------------------------------------------------------------------------------------
    # 이야기의 등장인물 데이터
    # ------------------------------------------------------------------------------------------
    if not data:
        data = " 1. 메리(주인공): 여자, 갈색 털, 8세, 토끼 2. 알렉스: 남자, 붉은 털, 9세, 다람쥐 3. 올빼미: 남자, 흰색 깃털, 10세, 부엉이 4. 거미 괴물: 성별 불명, 검은색 털, 나이 불명, 거미 괴물"
    # ------------------------------------------------------------------------------------------
    # 장면에 대한 분석과 stable diffusion에 맞는 프롬프트 생성
    # ------------------------------------------------------------------------------------------
    analysis_prompt = PromptTemplate.from_template(
        """
        분석할 텍스트:
        {content}

        당신은 텍스트를 분석하여 동화책 생성에 필요한 정보를 추출하는 전문가입니다.
        텍스트를 분석하여 다음 정보를 추출하세요:
        - 주인공은 반드시 포함
        - 등장인물 수
        - 등장인물의 이름, 성별, 종족, 나이, 머리색, 눈동자색
        - 상황, 배경, 사물
        - 텍스트 요약: 텍스트의 한 장면을 간략하게 작성
        - 테마 분석: 텍스트의 주요 주제와 배경
        - 분위기 분석: 감정적 톤과 분위기
        - 시각적 요소: 묘사된 장면, 캐릭터, 객체들
        - "characters" :"""+ data +"""의 데이터를 기반으로 등장인물 특징 작성

        """
    )



    image_prompt  = PromptTemplate.from_template(
        """
        분석 결과: 
        {analysis}

        당신은 분석 결과를 바탕으로 Stable Diffusion용 이미지 생성 프롬프트를 만드는 전문가입니다.
        정보를 추출하고 동화책 생성에 최적화된 프롬프트를 생성하세요:
        텍스트의 핵심 내용을 stable Diffusion에 최적화된 한 문장으로 요약

        **
        rule : 
        - 강조는 ((( )))로 작성.
        - 텍스트 요약으로 프롬프트 작성.
        - 주인공은 반드시 포함
        - 등장인물 수는 텍스트에서 나오는 인원의 수와 동일하게 작성.
        - 등장인물의 특징은 "characters"의 같은 이름이 가진 특징을 기준으로 강조 하여 작성
        - 동화풍으로 나올 수 있도록 프롬프트 작성.
        - "특징"에서의 "등장인물"이 사람인지 동물인지 분류.
        - Lora 모델은 : " https://civitai.com/models/1175678/caradhrasghibli-mix-style-or-illustrious" 모델 사용**.
        - "등장인물" 너무 크지 않게 프롬프트 작성.
        - "등장인물"과 "사물"의 크기 비율을 30%, 70%로 프롬프트 작성.
        - "등장인물"의 "성별" 등장인물이 남자면 "BOY", 여자면 "GIRL"로 프롬프트 작성.
        - "상황"과 "배경", "사물"을 강조하여 프롬프트 작성.
        - 중복된 프롬프트가 있으면 제거하고, 필요한 프롬프트만 작성
        - 주인공은 얼굴이 보이게 프롬프트 작성 
        - 태그는 짧게 작성하되, 필요한 정보는 모두 포함
        - 동화책의 이미지 생성에 최적화된 프롬프트 작성.
        - 장면이 한 장면만 나오도록 프롬프트 작성
        - 이 모든 것은 Stable Diffusion의 프롬프트 작성에 최적화된 형식으로 영어로 작성.
        **

        "
        긍정 프롬프트에 들어갈 내용: 
        - 긍정 프롬프트: """+ POSITIVE_PROMPT_BASE +""" 태그 포함
        - 상황, 배경, 캐릭터의 표정 stable diffusion에서 표현할수있는 최대강조로 프롬프트 작성(ex: "(((캐릭터의 표정))),(((상황))),(((배경)))" )
        - lora 모델에서 권장하는 프롬프트 추천하여 추가
        - 분석한 "테마"와 "분위기" 에 따라 lora모델의 분위기 설정 (ex: ("테마:subtle dark tone" = <lora:dark_fairy_tales:0.4>) )  
        - 품질 향상 키워드 포함 
        - "fairy-tale, children's illustration, style of children's book, dreamy, fantasy, poetry, nostalgic, water color" 중 상황에 맞게 태그 사용
        "
        
        "
        **rule**의 규칙에 따라 긍정 프롬프트와 부정 프롬프트를 작성 :
            - 긍정 프롬프트 : '긍정 프롬프트에 들어갈 내용'을 토대로 작성
        "
        
        **응답 형식 (반드시 올바른 JSON):**
        ```json
        {{
            "caption_text": "한글로 작성: caption_text",
            "labels": [한글로 작성: "label1", "label2"],
            "point": "한글로 작성: 등장인물의 이름, 성별, 종족,사물",
            "positive_prompt": "Stable Diffusion용 긍정 프롬프트",
        }}
        ```
        """
    )

    analysis_chain = analysis_prompt | model 
    image_chain = image_prompt | model

    # ------------------------------------------------------------------------------------------
    # illustration와 cover_illustration 여부 확인
    # ------------------------------------------------------------------------------------------
    if ((check) == "illustration"):
        analysis_response   = analysis_chain.invoke({
            "content": story_paragraph.content_text
        })

    elif ((check) == "cover_illustration"):
        analysis_response   = analysis_chain.invoke({
            "content": story.summary
        })

    if debug:
        print(f"content_text  응답: {analysis_response.content}")

    image_response = image_chain.invoke({"analysis": analysis_response.content})

    #--------------------------------------------------------------------------------
    # JSON 파싱 및 오류 처리
    #--------------------------------------------------------------------------------
    try:
        # 응답에서 JSON 부분만 추출
        content = image_response.content

        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
            print(f"[LLM 분석] json_content ##1: {json_content}")
        else:
            json_content = content

        result = json.loads(json_content)
        return result

    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        # 기본값 설정
        return {
            "caption_text": "caption_text",
            "labels": ["장면", "배경"],
            "positive_prompt": f"{POSITIVE_PROMPT_BASE} a scene inspired by: digital art, detailed, high quality",
        }
   