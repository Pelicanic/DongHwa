import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from api.models import Story, User
from django.db import connection
from django.utils import timezone


# Langgraph용
from api.services.langgraph.story_flow import story_flow
from api.models import User , Illustration, Storyparagraph, Paragraphqa
# from django.views.decorators.csrf import csrf_exempt

# 라이브러리 불러오기
# AI 라이브러리 연동
from api.services.chatbot_gemini_lib import vectordb_load, chat_query


if vectordb_load('rain') == False:
    print('VectorDB 로드 실패')
    exit()

# @csrf_exempt
@api_view(['GET']) # csrf_exempt 자동 적용됨
def index(request):
    return Response({"message": "DongHwa Backend API is running."})



# # 예제 코드 : 챗봇
# @api_view(['GET', 'POST'])
# def chat_v1(request):
#     try:
#         msg = request.data.get('msg', '')
#         if not msg:
#             return Response(
#                 {"code": -1, "msg": "메시지가 비어 있습니다."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         alresult = chat_query(msg)

#         return Response(
#             {"code": 1, "aimsg": alresult},
#             status=status.HTTP_200_OK
#         )

#     except Exception as e:
#         return Response(
#             {"code": -1, "msg": f"오류가 발생했습니다: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

@api_view(['POST'])
def story_select(request):
    try:
        story_id = request.data.get("story_id")
        if not story_id:
            return Response({"error": "story_id is required"}, status=400)

        datas = Paragraphqa.objects.raw("SELECT * FROM ParagraphQA WHERE story_id = %s", [story_id])
        list = []
        for data in datas:
            list.append({
                "qa_id": data.qa_id,
                "paragraph_id": data.paragraph_id,
                "story_id": data.story_id,
                "question_text": data.question_text,
                "answer_text": data.answer_text,
                "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "ai_question": data.ai_question,
                "answer_choice": data.answer_choice,
            })
        return Response({"paragraphQA": list})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


# 작성자 : 최재우
# 기능 : story_id 를 통해 StoryParagraph테이블 데이터 호출
# 마지막 수정일 : 2025-06-17
@api_view(['POST'])
def story_paragraphQA(request):
    try:
        story_id = request.data.get("story_id")

        datas = Paragraphqa.objects.raw("SELECT * FROM ParagraphQA WHERE story_id = %s", [story_id])
        list = []
        for data in datas:
            list.append({
                "qa_id": data.qa_id,
                "paragraph_id": data.paragraph_id,
                "story_id": data.story_id,
                "question_text": data.question_text,
                "answer_text": data.answer_text,
                "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "ai_question": data.ai_question,
                "answer_choice": data.answer_choice,
            })
        return Response({"paragraphQA": list})
    
    except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
    
# 작성자 : 최재우
# 기능 : story_id 를 통해 StoryParagraph테이블 데이터 호출
# 마지막 수정일 : 2025-06-19
@api_view(['POST'])
def story_storyParagraph(request):
    try:
        story_id = request.data.get("story_id")

        datas = Storyparagraph.objects.raw("SELECT * FROM StoryParagraph WHERE story_id = %s ORDER BY paragraph_no", [story_id])
        list = []
        for data in datas:
            list.append({
                "paragraph_id": data.paragraph_id,
                "story_id": data.story_id,
                "paragraph_no": data.paragraph_no,
                "content_text": data.content_text,
                "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": data.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        # 빈 데이터 처리
        if not list:
            return Response({
                "storyParagraph": [],
                "message": "해당 스토리에 대한 문단이 없습니다.",
                "isEmpty": True
            })
        
        return Response({
            "storyParagraph": list,
            "isEmpty": False,
            "count": len(list)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "error": str(e),
            "storyParagraph": [],
            "isEmpty": True
        }, status=500)
    
# 작성자 : 최재우
# 기능 : story_id 를 통해 Illustration테이블 데이터 호출
# 마지막 수정일 : 2025-06-19
@api_view(['POST'])
def story_illustration(request):
    try:
        story_id = request.data.get("story_id")

        datas = Illustration.objects.raw("SELECT * FROM Illustration WHERE story_id = %s", [story_id])
        print(f"datIllustrationas: {datas}")

        list = []
        for data in datas:
            list.append({
                "illustration_id": data.illustration_id,
                "paragraph_id": data.paragraph_id,
                "story_id": data.story_id,
                "image_url": data.image_url,
                "caption_text": data.caption_text,
                "labels": data.labels,
                "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return Response({"illustration": list})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

# 작성자 : 최재우
# 기능 : story_id 를 통해 Story테이블 데이터 호출
# 마지막 수정일 : 2025-06-17
@api_view(['POST'])
def list_story(request):
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id is required"}, status=400)
    
    user = User.objects.get(user_id=user_id)
    stories = Story.objects.filter(author_user=user).order_by('-created_at')[:4]

    story_list = []
    for story in stories:
        story_list.append({
            "story_id": story.story_id,
            "author_user": story.author_user_id,
            "title": story.title,
            "summary": story.summary,
            "created_at": story.created_at,
            "updated_at": story.updated_at,
            "status": story.status,
            "author_name": story.author_name,
            "age": story.age,
            "cover_img": story.cover_img,
            "characters": story.characters
        })
    
    return Response({"stories": story_list})


# LangGraph 실행 객체 초기화
flow = story_flow()

# 작성자 : 최준혁
# 기능 : story_id 생성
# 마지막 수정일 : 2025-06-03
def get_next_story_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(story_id) FROM Story")
        row = cursor.fetchone()
        return (row[0] or 0) + 1


# 작성자 : 최준혁
# 기능 : news 페이지에서 호출하는 LangGraph 기반 동화 생성 API
# 마지막 수정일 : 2025-06-03
@api_view(['POST'])
def chatbot_story(request):
    try:
        user_id = request.data.get("user_id")
        story_id = request.data.get("story_id")
        paragraph_id = request.data.get("paragraph_id")
        mode = request.data.get("mode", "create")
        user_input = request.data.get("user_input")
        paragraph_no = request.data.get("paragraph_no")
        answers = request.data.get("answers")

        # 필요한 추가 처리 로직 예시 (input 구성 등)
        if paragraph_no == "1" and answers:
            answers = request.data.get("answers")
            # answers에서 개별 항목 추출
            fairy_tale = answers.get("0")
            theme = answers.get("1")
            mood = answers.get("2")
            character_name = answers.get("3")
            character_age = answers.get("4")
            user_input = f"'{fairy_tale}'풍의 이야기, Theme: {theme}, Mood: {mood}, 주인공 이름: '{character_name}', 주인공의 나이: '{character_age}'살로 동화를 만들고싶어."
        elif not user_input:
            user_input = ""
            


        user = User.objects.get(user_id=user_id)

        # story_id가 없다면 새로 생성
        if not story_id:
            story_id = get_next_story_id()
            Story.objects.create(
                story_id=story_id,
                author_user=user,
                title="제목 없음",
                created_at=timezone.now(),
                updated_at=timezone.now(),
                status="in_progress",
                author_name=user.nickname,
                age=user.age
            )

        # LangGraph 초기 상태
        initial_state = {
            "input": user_input,
            "user_id": user_id,
            "story_id": story_id,
            "age": user.age,
            "mode": mode,
        }
        if mode == "edit" and paragraph_id:
            initial_state["paragraph_id"] = paragraph_id

        result = flow.invoke(initial_state)


        return Response({
            "story_id": story_id,
            "paragraph": result.get("paragraph_text"),
            "paragraph_no": result.get("paragraph_no"),
            "version_no": result.get("version_no"),
            "paragraph_id": result.get("paragraph_id")
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)



    
    

    


    
    