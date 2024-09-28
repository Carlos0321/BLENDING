from django.shortcuts import render
from django.http import JsonResponse
import speech_recognition as sr

def audio_to_text(request):
    if request.method == 'POST':
        # 오디오 파일을 받고 처리
        audio_file = request.FILES['audio']
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        try:
            # SpeechRecognition 라이브러리를 사용하여 텍스트 변환
            text = recognizer.recognize_google(audio)
            return JsonResponse({'text': text}, safe=False)
        except sr.UnknownValueError:
            return JsonResponse({'error': 'Audio not understandable'}, safe=False)
        except sr.RequestError:
            return JsonResponse({'error': 'Failed to get results'}, safe=False)
    return render(request, 'index.html')
