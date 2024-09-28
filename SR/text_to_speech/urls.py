# text_to_speech/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('speak/', views.text_to_audio, name='convert_text_to_audio'),
]
