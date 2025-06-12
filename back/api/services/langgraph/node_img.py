# 작성자 : 최재우
# 작성일 : 2025-06-11
import google.generativeai as genai
import os
import re
import json

from typing import Tuple, List, Dict

from api.models import Paragraphqa, Storyparagraph, Paragraphversion
from api.services.vector_utils import get_latest_paragraphs
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

debug = True

# ------------------------------------------------------------------------------------------
# Gemini 초기화 및 모델 정의
# ------------------------------------------------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    streaming=False
)

# ------------------------------------------------------------------------------------------
# 패러그래프 생성 관련
# ------------------------------------------------------------------------------------------
def generate_image(state: dict) -> dict:
    story_id = state.get("story_id")
    paragraph_id = state.get("paragraph_id")

    story_paragraph = Storyparagraph.objects.get(paragraph_id=paragraph_id)


# ------------------------------------------------------------------------------------------
# LLM 분석 및 이미지 생성 파이프라인
# ------------------------------------------------------------------------------------------
    prompt = PromptTemplate.from_template(
        """
        당신은 텍스트를 분석하여 Stable Diffusion용 이미지 생성 프롬프트를 만드는 전문가입니다.
        주어진 텍스트를 분석하여 다음 정보를 추출하고 동화책 생성에 최적화된 프롬프트를 생성하세요:
       
        
        **분석 항목:
        - 등장 : 등장인물의 몇명인지, 이름, 성별, 종족, 상황, 배경, 사물
        - 테마 분석: 텍스트의 주요 주제와 배경
        - 분위기 분석: 감정적 톤과 분위기
        - 시각적 요소: 묘사된 장면, 캐릭터, 객체들
        - 스타일 힌트: 예술 스타일이나 시각적 특성
        - 텍스트 요약 텍스트의 핵심 내용 한 문장으로 요약
        **

        **
        설정 : 
        - 텍스트 요약으로 프롬프트 작성.
        - Stable Diffusion의 프롬프트 작성에 최적화된 형식으로 작성.
        - 동화풍으로 나올 수 있도록 프롬프트 작성.
        - "등장"에서의 "등장인물"이 사람인지 동물인지 분류.
        - "등장"에서의 "등장인물"이 사람이라면 Lora 모델은 : " https://civitai.com/models/1175678/caradhrasghibli-mix-style-or-illustrious" 모델 사용**.
        - "등장"에서의 "등장인물"이 동물이라면 Lora 모델은 : " https://civitai.com/models/1320017/cute-animal-illustration " 모델 사용**.
        - "등장"에서의 "등장인물" 너무 크지 않게 프롬프트 작성.
        - "등장"에서의 "등장인물"과 "사물"의 크기 비율을 30%, 70%로 프롬프트 작성.
        - 텍스트를 분석하여 "등장"에서의 "등장인물"의 "성별" 등장인물이 남자면 "BOY", 여자면 "GIRL"로 프롬프트 작성.
        - Stable Diffusion의 프롬프트 작성 시 "등장"에서의 "등장인물"은 반드시 포함하고, 분석한 "상황"과 "배경", "사물"을 강조하여 프롬프트 작성.
        - 중복된 프롬프트가 있으면 제거하고, 필요한 프롬프트만 작성
        - 등장인물은 얼굴이 보이게 프롬프트 작성 
        - 프롬프트는 짧게 작성하되, 필요한 정보는 모두 포함
        - 동화책의 이미지 생성에 최적화된 프롬프트 작성.
        - 프롬프트는 동화책의 일러스트레이션에 적합하도록 작성
        - 등장인물 수와 종족, 성별을 명확히 하는 프롬프트 작성
        **

        "
        긍정 프롬프트에 들어갈 내용: 
        - ((masterpiece)), ((best quality)), ((detailed)), ((highly detailed)), ((cinematic lighting)), 4K
        - 텍스트 요약 한 문장으로 프롬프트 작성
        - 상황, 배경, 캐릭터의 표정 stable diffusion에서 표현할수있는 최대강조로 프롬프트 작성(ex: "(((캐릭터의 표정))),(((상황))),(((배경)))" )
        - stable diffusion의 Lora 모델을 사용하여 이미지 프롬프트 작성
        - lora 모델에서 권장하는 프롬프트 추천하여 추가
        - 분석한 "테마"와 "분위기" 에 따라 lora모델의 분위기 설정 (ex: ("테마:subtle dark tone" = <lora:dark_fairy_tales:0.4>) )  
        - 품질 향상 키워드 포함 
        - 장면이 한 장면만 나오도록 프롬프트 작성
        - 프롬프트 중복되지않게 작성
        - 등장인물 반드시 포함
        - "fairy-tale, children's illustration, style of children's book, dreamy, fantasy, poetry, nostalgic, water color" 중 상황에 맞게 태그 사용
        "
        " 
        부정 프롬프트에 들어갈 내용: 
            - 부정적인 요소 상세히 표시
            - 부정적 요소는 negative prompt로 별도 제안
            - 사물이 등장인물에 비해 과하게 크지 않도록 프롬프트 작성
            - 품질 저하 요소는 부정 프롬프트로 제안 (예: "blurry", "low quality", "distorted", "ugly")
            - 오류 나 왜곡된 이미지 요소는 부정 프롬프트로 제안 (예: "bad anatomy", "bad proportions", "extra limbs")
            - 불필요한 요소 제거 (예: "watermark", "signature", "text")
            - 부정 프롬프트 "((half animal)),(( animal hybrid)),animal transformation, were-, lycanthrope, centaur, satyr, minotaur", extra ears, double ears, four ears, multiple ears, artificial, bad quality, bad perspective, bad geometry, worst depth, bad depth, bad dynamics, generic, fused, jpeg artifacts, (missing fingers:1.2), (multiple_views:1.4), downscaled, shortstack, short_stack, loli, child, teen, oldest, lolita, unfinished, duplicated, (extra fingers:1.2), extra digits, artist_name, patreon_logo, signature, watermark, twitter_logo, twitter_name, (long-legs:1.3), (short-torso:1.1), sound_effects, speech_bubble, mosaic_censoring, censoredartificial, censored, (duplicated navel:1.4), ugly, deformed, noisy, low poly, blurry, worst quality, multiple angle, split view, ((looking at viewer)), bad fingers, blue_archive, halo, backlighting, bad lighting, poorly drawn teeth, poorly drawn mouth, close up, (extreme close up), upscaled, fused details, portrait, ai generated, ai assisted, perfect lines, low quality, negative_hand, bad-hands-4, x-ray, futanari, monochrome, greyscale, cross, sepia, lineart, outlines, painting, drawing, illustration, blurry face, clipping, ugly face, glowing hands, extra arms, muscular, deformed body, patreon username, 3d, choker, artist name, capelet, simple background, deformities, b&w, bad hands, poorly drawn hands, too many fingers, too few fingers, badly drawn fingers, bad feet, deformed feet, bad toes, deformed toes, too many toes, too few toes, more than 5 toes, less than 5 toes, excessive number of toes, feet on wrong leg, feet facing wrong direction, backwards feet, too many feet, text, numbers, heart, patreon, twitter, subscribestar, roads, worst detail, sketch, censor, animal, too many, monster, thick, anthro, furry, speech bubbles, writing, dickgirl, (fewer digits:1.3), (duplicated navel:1.1), selfie, see-through_clothes, wet, oily, shiny_skin, painted, clothed animal, side view, realistic, creature, lowres, artistic error, multiple views, displeasing, worst aesthetic, old, early, (multiple girls, multiple boys):1.7, (solo, threesome, three people:1.3), penis lettering, text bubbles, see-through, xray, bad anatomy, duplicate, twin, mirroring, (easynegative, lazyneg, safe_neg, ng_deepnegative_v1_75t), longbody, pubic hair, cropped, extra digit, fewer digits, missing fingers, username, logo, sign, extra limbs, bad art, fused hands, bad proportions, broken finger, distorted hands, compression artifacts, flowers, roses, crown, diadem, masculine, (solo:1.3), (worst quality:2), (low quality:2), out of focus, deformed eyes, bad composition, cartoon style, missing details, poor lighting, flat shading, cluttered background, poor texture, inconsistent style, simple serpent, oversaturated colors, SmoothNoob_Negative, SmoothNegative_Hands-neg, abstract, surreal, messy, (bad eyes), (cross-eyed), (fused eyes), (asymmetrical eyes), (wrong eye direction), (lazy eye), (blurry eyes), (bad nose), (deformed nose), (flat nose), (asymmetrical nose), (bad mouth), (deformed mouth), (fused lips), (missing mouth), (asymmetrical mouth), ((half animal)), (( animal hybrid)), animal transformation, were-, lycanthrope, centaur, satyr, minotaur, distorted, nsfw, nude, naked, sex, sexual, panties, nipples, areola, cleavage, breast, pussy, thong, lingerie, erotic, porn, lewd, suggestive, uncensored, exposed, crotch, underboob, undergarments, transparent clothing" 태그 포함
        "
        
        "
        **설정**의 규칙에 따라 긍정 프롬프트와 부정 프롬프트를 작성 :
            - 긍정 프롬프트 : '긍정 프롬프트에 들어갈 내용'을 토대로 작성
            - 부정 프롬프트 : '부정 프롬프트에 들어갈 내용'을 토대로 작성
        "


            
        **응답 형식 (반드시 올바른 JSON):**
        ```json
        {{
            "theme": "추출된 테마",
            "mood": "추출된 분위기", 
            "등장: "등장인물의 이름, 성별, 종족","사물"
            "텍스트 요약": "텍스트의 핵심 내용 요약",
            "상황에 맞게 태그 사용": ["태그1", "태그2"],
            "positive_prompt": "Stable Diffusion용 긍정 프롬프트",
            "negative_prompt": "Stable Diffusion용 부정 프롬프트"
        }}
        ```
        분석할 텍스트:
        {content}
        """
    )

    chain = prompt | model

    print(f"[LLM 분석] 원본 텍스트: {story_paragraph.content_text}")
    response = chain.invoke({
        "content": story_paragraph.content_text
    })
    
    if debug:
        print(f"[LLM 분석] 원본 응답: {response.content}")


    #--------------------------------------------------------------------------------
    # JSON 파싱 및 오류 처리
    #--------------------------------------------------------------------------------
    try:
        # 응답에서 JSON 부분만 추출
        content = response.content
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
            print(f"[LLM 분석] json_content ##1: {json_content}")
        elif "{" in content and "}" in content:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_content = content[json_start:json_end]
            print(f"[LLM 분석] json_content ##2: {json_content}")
        else:
            json_content = content
        
        analysis_result = json.loads(json_content)
        
        if debug:
            print(f"[LLM 분석] 파싱된 결과: {analysis_result}")
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        if debug:
            print(f"[LLM 분석] JSON 파싱 실패: {e}")
        
        # 파싱 실패 시 기본값 반환
            return create_fallback_analysis()
    
    #--------------------------------------------------------------------------------
    # LLM 분석 실패 시 기본 분석 결과 생성
    #--------------------------------------------------------------------------------
    def create_fallback_analysis() -> Dict:
        return {
            "theme": "일반적인 장면",
            "mood": "중성적인",
            "visual_elements": ["장면", "배경"],
            "positive_prompt": "a scene inspired by: digital art, detailed, high quality",
            "negative_prompt": "blurry, low quality, distorted, ugly",
            "style_tags": ["digital art", "detailed"]
        }
    



    def generate_image_with_stable_diffusion(
                                           positive_prompt: str, 
                                           negative_prompt: str = "",
                                           width: int = 1024,
                                           height: int = 1024,
                                           steps: int = 30,
                                           cfg_scale: float = 7.0) -> Dict[str, Any]:
        """
        Stable Diffusion API를 사용하여 이미지 생성
        """
        try:
            if debug:
                print(f"[Stable Diffusion] 긍정 프롬프트: {positive_prompt}")
                print(f"[Stable Diffusion] 부정 프롬프트: {negative_prompt}")
            
            # Stability AI API 엔드포인트
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {stability_api_key}",
            }
            
            # API 요청 데이터
            body = {
                "text_prompts": [
                    {
                        "text": positive_prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": steps,
                "seed": 0,  # 랜덤 시드
                "style_preset": "digital-art"  # 스타일 프리셋
            }
            
            # 부정 프롬프트 추가
            if negative_prompt:
                body["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            if self.debug:
                print(f"[Stable Diffusion] API 요청: {json.dumps(body, indent=2)}")
            
            # API 호출
            response = requests.post(url, headers=headers, json=body)
            
            if self.debug:
                print(f"[Stable Diffusion] 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 첫 번째 이미지 처리
                if data.get("artifacts") and len(data["artifacts"]) > 0:
                    image_data = data["artifacts"][0]
                    base64_image = image_data["base64"]
                    
                    # Base64를 이미지 파일로 저장
                    image_url = self._save_base64_image(base64_image)
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "image_data": base64_image,
                        "seed": image_data.get("seed"),
                        "finish_reason": image_data.get("finishReason")
                    }
                else:
                    return {
                        "success": False,
                        "error": "이미지 데이터를 받지 못했습니다",
                        "response": data
                    }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": f"API 호출 실패: {response.status_code}",
                    "details": error_data
                }
                
        except Exception as e:
            if self.debug:
                print(f"[Stable Diffusion] 오류: {e}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_base64_image(self, base64_string: str, 
                          save_dir: str = "generated_images") -> str:
        """
        Base64 인코딩된 이미지를 파일로 저장하고 경로 반환
        """
        try:
            # 저장 디렉토리 생성
            os.makedirs(save_dir, exist_ok=True)
            
            # Base64 디코딩
            image_data = base64.b64decode(base64_string)
            
            # PIL Image로 변환
            image = Image.open(io.BytesIO(image_data))
            
            # 파일명 생성 (타임스탬프 기반)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            
            # 이미지 저장
            image.save(filepath, "PNG")
            
            if self.debug:
                print(f"[이미지 저장] 파일 저장됨: {filepath}")
            
            return filepath
            
        except Exception as e:
            if self.debug:
                print(f"[이미지 저장] 오류: {e}")
            return "error_saving_image.png"
    
    def process_text_to_image(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        전체 파이프라인 실행: 텍스트 → LLM 분석 → 이미지 생성
        """
        pipeline_start = datetime.now()
        
        if self.debug:
            print(f"[파이프라인 시작] 텍스트: {text[:50]}...")
        
        # 1단계: LLM으로 텍스트 분석
        analysis = self.analyze_text_with_llm(text)
        
        # 2단계: Stable Diffusion으로 이미지 생성
        generation_params = {
            "positive_prompt": analysis["positive_prompt"],
            "negative_prompt": analysis.get("negative_prompt", ""),
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "steps": kwargs.get("steps", 30),
            "cfg_scale": kwargs.get("cfg_scale", 7.0)
        }
        
        image_result = self.generate_image_with_stable_diffusion(**generation_params)
        
        pipeline_end = datetime.now()
        processing_time = (pipeline_end - pipeline_start).total_seconds()
        
        # 결과 조합
        final_result = {
            "original_text": text,
            "analysis": analysis,
            "image_generation": image_result,
            "processing_time": processing_time,
            "timestamp": pipeline_end.isoformat()
        }
        
        if self.debug:
            print(f"[파이프라인 완료] 처리 시간: {processing_time:.2f}초")
            print(f"[파이프라인 완료] 성공 여부: {image_result.get('success', False)}")
        
        return final_result

# ===== LangGraph 노드 함수로 통합 =====

def generate_image_from_text(state: dict, debug: bool = False) -> dict:
    """
    LangGraph 노드 함수: 텍스트 기반 이미지 생성
    
    Parameters:
    -----------
    state : dict
        - text: 분석할 텍스트 (필수)
        - openai_api_key: OpenAI API 키 (필수)
        - stability_api_key: Stability AI API 키 (필수)
        - width: 이미지 너비 (선택, 기본값: 1024)
        - height: 이미지 높이 (선택, 기본값: 1024)
        - steps: 생성 스텝 수 (선택, 기본값: 30)
        - cfg_scale: CFG 스케일 (선택, 기본값: 7.0)
    
    Returns:
    --------
    dict : 업데이트된 상태
        - theme: LLM이 추출한 테마
        - mood: LLM이 추출한 분위기
        - image_url: 생성된 이미지 파일 경로
        - positive_prompt: 사용된 긍정 프롬프트
        - negative_prompt: 사용된 부정 프롬프트
        - generation_success: 이미지 생성 성공 여부
        - processing_time: 처리 시간
        - error: 오류 메시지 (있는 경우)
    """
    
    # 필수 파라미터 확인
    text = state.get("text")
    openai_api_key = state.get("openai_api_key")
    stability_api_key = state.get("stability_api_key")
    
    if not text:
        return {
            "error": "텍스트가 제공되지 않았습니다",
            "generation_success": False
        }
    
    if not openai_api_key or not stability_api_key:
        return {
            "error": "API 키가 제공되지 않았습니다",
            "generation_success": False
        }
    
    try:
        # 파이프라인 초기화
        pipeline = TextToImagePipeline(
            openai_api_key=openai_api_key,
            stability_api_key=stability_api_key,
            debug=debug
        )
        
        # 이미지 생성 실행
        result = pipeline.process_text_to_image(
            text=text,
            width=state.get("width", 1024),
            height=state.get("height", 1024),
            steps=state.get("steps", 30),
            cfg_scale=state.get("cfg_scale", 7.0)
        )
        
        # 결과 파싱
        analysis = result["analysis"]
        image_gen = result["image_generation"]
        
        # 상태 업데이트 반환
        return {
            "theme": analysis["theme"],
            "mood": analysis["mood"],
            "visual_elements": analysis["visual_elements"],
            "style_tags": analysis["style_tags"],
            "positive_prompt": analysis["positive_prompt"],
            "negative_prompt": analysis["negative_prompt"],
            "image_url": image_gen.get("image_url") if image_gen.get("success") else None,
            "image_data": image_gen.get("image_data") if image_gen.get("success") else None,
            "generation_success": image_gen.get("success", False),
            "processing_time": result["processing_time"],
            "error": image_gen.get("error") if not image_gen.get("success") else None,
            "seed": image_gen.get("seed"),
            "finish_reason": image_gen.get("finish_reason")
        }
        
    except Exception as e:
        if debug:
            print(f"[노드 함수] 오류 발생: {e}")
        
        return {
            "error": str(e),
            "generation_success": False
        }


        # # illustration 테이블에 저장
        # illustration = Storyparagraph.objects.create(
        #     story_id = story_id,
        #     paragraph_id = paragraph_id,
        #     image_url = image_url,
        #     caption_text = caption_text,
        #     labels = labels,
        # )




    # theme = state.get("theme", "판타지 (SF/이세계)")
    # mood = state.get("mood", "신비로운")
    # labels = find_labels_by_theme_and_mood(theme, mood)



    # # 디버깅용
    # if debug:
    #     print(f"[GenerateImage] 이미지 URL: {image_url}, caption: {caption_text}")
    #     print(f"[GenerateParagraph] theme: {theme}, mood: {mood}")



    # return {
    #     "image_url": f"https://dummyimage.com/600x400/000/fff&text=Image",
    #     "caption": f"{theme} 테마의 {mood} 분위기를 담은 이미지",
    #     "labels": labels
    # }


# def find_labels_by_theme_and_mood(theme: str, mood: str) -> list:
#     for (key_theme, key_mood), labels in THEME_MOOD_LABELS.items():
#         if key_theme == theme and key_mood == mood:
#             return labels
#     return ["기본", "이미지", "라벨"]