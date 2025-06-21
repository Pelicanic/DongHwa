from django.urls import path
from . import views
from .views import chatbot_story, list_story, story_illustration, story_storyParagraph, story_paragraphQA, story_story

urlpatterns = [
    path('', views.index, name='api_index'),
    path('v1/chat/story/', chatbot_story, name='api_chatbot_story'),
    path('v1/main/story/', list_story, name='api_list_story'),

    # 작성자 : 최재우
    # 마지막 수정일 : 2025-06-17
    # 기능 : 일러스트 값 호출
    path('v1/illustration/story/', story_illustration, name='api_story_illustration'),
     # 작성자 : 최재우
    # 마지막 수정일 : 2025-06-17
    # 기능 : 문단 값 호출
    path('v1/storyParagraph/story/', views.story_storyParagraph, name='api_story_storyParagraph'),
    # 작성자 : 최재우
    # 마지막 수정일 : 2025-06-17
    path('v1/paragraphQA/story/', views.story_paragraphQA, name='api_story_paragraphQA'),
    # 작성자 : 최재우

    # 마지막 수정일 : 2025-06-21
    path('v1/story/story/', views.story_story, name='api_story_story'),
]


