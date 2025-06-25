from django.urls import path
from . import views
from .views import chatbot_story, list_story, story_illustration, story_storyParagraph, story_paragraphQA, story_story, list_story_by_status, search_stories, get_user_in_progress_story, get_random_published_titles

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
    path('v1/storyParagraph/story/', story_storyParagraph, name='api_story_storyParagraph'),
    # 작성자 : 최재우
    # 마지막 수정일 : 2025-06-17
    path('v1/paragraphQA/story/', story_paragraphQA, name='api_story_paragraphQA'),
    # 작성자 : 최재우
    # 마지막 수정일 : 2025-06-21
    # 기능 : 동화 조회
    # story_id를 통해 동화 조회
    path('v1/story/story/', story_story, name='api_story_story'),
    # 작성자 : Assistant
    # 마지막 수정일 : 2025-06-23
    # 기능 : status 조건에 따른 동화 목록 조회
    path('v1/list/story/', list_story_by_status, name='api_list_story_by_status'),
    # 작성자 : Assistant
    # 마지막 수정일 : 2025-06-25
    # 기능 : 동화 검색 (제목 또는 작성자 닉네임)
    path('v1/search/story/', search_stories, name='api_search_stories'),
    # 작성자 : Assistant
    # 마지막 수정일 : 2025-06-25
    # 기능 : 사용자의 진행 중인 동화 조회
    path('v1/user/in-progress-story/', get_user_in_progress_story, name='api_get_user_in_progress_story'),
    # 작성자 : Assistant
    # 마지막 수정일 : 2025-06-25
    # 기능 : published 상태의 동화 제목 랜덤 3개 조회
    path('v1/random/published-titles/', get_random_published_titles, name='api_get_random_published_titles'),
]


