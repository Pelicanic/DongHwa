from django.urls import path
from . import views
from .views import chatbot_story, list_story

urlpatterns = [
    path('', views.index, name='api_index'),
    path('v1/chat/story/', chatbot_story, name='api_chatbot_story'),
    path('v1/main/story/', list_story, name='api_list_story')

]


