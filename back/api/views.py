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


# 작성자 : Assistant
# 기능 : published 상태의 동화 제목 랜덤 3개 조회
# 마지막 수정일 : 2025-06-25
@api_view(['GET'])
def get_random_published_titles(request):
    try:
        # published 상태의 동화들 중에서 제목이 있는 것들 조회
        published_stories = Story.objects.filter(
            status='published',
            title__isnull=False
        ).exclude(
            title=''
        ).values_list('title', flat=True)
        
        if len(published_stories) < 3:
            # 데이터가 3개 미만일 때 기본값 반환
            return Response({
                "success": True,
                "titles": ["여우와 두루미", "개미와 베짱이", "토끼와 거북이"]
            })
        
        # 랜덤으로 3개 선택
        import random
        random_titles = random.sample(list(published_stories), min(3, len(published_stories)))
        
        return Response({
            "success": True,
            "titles": random_titles
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


# 작성자 : Assistant
# 기능 : 사용자의 가장 최신 동화가 in_progress인지 확인
# 마지막 수정일 : 2025-06-25
@api_view(['POST'])
def get_user_in_progress_story(request):
    try:
        user_id = request.data.get("user_id")
        
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)
        
        # 사용자의 모든 동화 중 가장 최신 것 조회 (status 무관)
        latest_story = Story.objects.filter(
            author_user_id=user_id
        ).order_by('-updated_at').first()
        
        if not latest_story:
            # 아예 동화가 없는 경우
            return Response({
                "success": False,
                "message": "동화가 없습니다.",
                "story": None,
                "reason": "no_stories"
            })
        
        # 가장 최신 동화의 상태 확인
        if latest_story.status == 'in_progress':
            # 가장 최신 동화가 진행 중인 경우
            story_data = {
                "story_id": latest_story.story_id,
                "author_user": latest_story.author_user_id,
                "title": latest_story.title,
                "summary": latest_story.summary,
                "summary_4step": latest_story.summary_4step,
                "created_at": latest_story.created_at,
                "updated_at": latest_story.updated_at,
                "status": latest_story.status,
                "author_name": latest_story.author_name,
                "age": latest_story.age,
                "cover_img": latest_story.cover_img,
                "characters": latest_story.characters
            }
            
            return Response({
                "success": True,
                "message": "진행 중인 동화를 찾았습니다.",
                "story": story_data
            })
        else:
            # 가장 최신 동화가 completed이거나 다른 상태인 경우
            return Response({
                "success": False,
                "message": f"가장 최신 동화의 상태가 '{latest_story.status}' 입니다.",
                "story": None,
                "reason": "latest_not_in_progress",
                "latest_status": latest_story.status
            })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


# 작성자 : 최재우
# 기능 : 제목 또는 유저 닉네임으로 동화 검색 (exbook과 libbook 대상)
# 마지막 수정일 : 2025-06-25
@api_view(['POST'])
def search_stories(request):
    try:
        query = request.data.get("query", "").strip()
        page = request.data.get("page", 1)
        page_size = request.data.get("page_size", 10)
        
        if not query:
            return Response({"error": "검색어가 필요합니다."}, status=400)
        
        # exbook (status='published')과 libbook (status='completed') 데이터 검색
        # 제목 또는 작성자 닉네임으로 검색
        with connection.cursor() as cursor:
            # 전체 검색 결과 수 조회
            count_sql = """
                SELECT COUNT(*) 
                FROM Story s 
                JOIN User u ON s.author_user_id = u.user_id 
                WHERE (s.status = 'published' OR s.status = 'completed') 
                AND (s.title LIKE %s OR u.nickname LIKE %s)
            """
            cursor.execute(count_sql, [f'%{query}%', f'%{query}%'])
            total_count = cursor.fetchone()[0]
            
            # 페이징 계산
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # 검색 결과 조회 (페이징 적용)
            search_sql = """
                SELECT s.*, u.nickname as author_nickname
                FROM Story s 
                JOIN User u ON s.author_user_id = u.user_id 
                WHERE (s.status = 'published' OR s.status = 'completed') 
                AND (s.title LIKE %s OR u.nickname LIKE %s)
                ORDER BY s.updated_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(search_sql, [f'%{query}%', f'%{query}%', page_size, offset])
            
            stories_data = cursor.fetchall()
            
            # 결과 포맷팅
            story_list = []
            for row in stories_data:
                story_list.append({
                    "story_id": row[0],
                    "author_user": row[1],
                    "title": row[2],
                    "summary": row[3],
                    "summary_4step": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "status": row[7],
                    "author_name": row[8],
                    "age": row[9],
                    "cover_img": row[10],
                    "characters": row[11],
                    "author_nickname": row[12]
                })
        
        return Response({
            "stories": story_list,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "search_query": query
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


# 작성자 : 최재우
# 기능 : story_id 를 통해 Story 테이블 데이터 호출
# 마지막 수정일 : 2025-06-21
@api_view(['POST'])
def story_story(request):
    try:
        story_id = request.data.get("story_id")
        if not story_id:
            return Response({"error": "story_id is required"}, status=400)

        # Story 테이블에서 story_id로 데이터 조회
        try:
            story = Story.objects.raw("SELECT * FROM Story WHERE story_id = %s", [story_id])[0]
        except Story.DoesNotExist:
            return Response({"error": "Story not found"}, status=404)

        # 데이터 반환
        response_data = {
            "story_id": story.story_id,
            "author_user_id": story.author_user_id,
            "title": story.title,
            "summary": story.summary,
            "created_at": story.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": story.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": story.status,
            "author_name": story.author_name,
            "age": story.age,
            "cover_img": story.cover_img,
            "characters": story.characters
        }

        return Response({"story": response_data})

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
                "tts": data.tts,
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


# 작성자 : 최재우
# 기능 : status 조건에 따른 동화 목록 조회 (페이징 지원)
# 마지막 수정일 : 2025-06-23
@api_view(['POST'])
def list_story_by_status(request):
    try:
        status = request.data.get("status")
        page = request.data.get("page", 1)  # 기본값 1페이지
        page_size = request.data.get("page_size", 10)  # 기본값 10개씩
        
        if not status:
            return Response({"error": "status is required"}, status=400)
        
        # status 조건에 맞는 전체 동화 수 조회
        total_count = Story.objects.filter(status=status).count()
        
        # 페이징 계산
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size  # 올림 계산
        
        # status 조건에 맞는 동화 조회 (페이징 적용)
        stories = Story.objects.filter(status=status).order_by('-created_at')[offset:offset + page_size]

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
        
        return Response({
            "stories": story_list,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


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
            character_gender = answers.get("4")
            user_input = f"'{fairy_tale}'풍의 이야기, Theme: {theme}, Mood: {mood}, 주인공 이름: '{character_name}', 주인공의 성별: '{character_gender}'로 동화를 만들고싶어."
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