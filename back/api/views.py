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
from api.models import User
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



# 예제 코드 : 챗봇
@api_view(['GET', 'POST'])
def chat_v1(request):
    try:
        msg = request.data.get('msg', '')
        if not msg:
            return Response(
                {"code": -1, "msg": "메시지가 비어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        alresult = chat_query(msg)

        return Response(
            {"code": 1, "aimsg": alresult},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"code": -1, "msg": f"오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



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
        user_input = request.data.get("input")

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
            "theme": request.data.get("theme"),
            "mood": request.data.get("mood"),
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
