# back/tts/urls.py
from django.urls import path
from .views import generate_story_audio, stream_qa_audio

urlpatterns = [
    path("generate/", generate_story_audio, name="generate_story_audio"),
    path("qa-audio/<int:qa_id>/", stream_qa_audio, name="stream-qa-audio"),
]

