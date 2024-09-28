# voice_transcription/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'speech_to_text',
    'text_to_speech',
    # 다른 필수 앱들
]
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'yourwebsite.com']
