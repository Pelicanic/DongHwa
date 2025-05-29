import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
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

