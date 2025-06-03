from django.urls import path
from . import views
from .views import chatbot_story

urlpatterns = [
    path('', views.index, name='api_index'),
    path('v1/chat/', views.chat_v1, name='api_chat'),
    path('v1/chat/story/', chatbot_story, name='api_chatbot_story'),

]
