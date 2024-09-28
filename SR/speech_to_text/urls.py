# speech_to_text/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('convert/', views.audio_to_text, name='convert_audio_to_text'),
]
