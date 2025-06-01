from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='api_index'),
    path('v1/chat/', views.chat_v1, name='api_chat'),
    
]