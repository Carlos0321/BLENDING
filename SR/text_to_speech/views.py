from django.shortcuts import render
from django.http import JsonResponse
from gtts import gTTS
import os

def text_to_audio(request):
    text = request.GET.get('text', None)
    if text:
        tts = gTTS(text, lang='en')
        tts.save('output.mp3')
        return JsonResponse({'message': 'Conversion successful', 'url': '/static/output.mp3'}, safe=False)
    return render(request, 'index.html', {'error': 'No text provided'})
