from google.cloud import speech

def speech_to_text_conversion(audio_file):
    """Google Cloud Speech-to-Text API를 사용하여 오디오 파일의 음성을 텍스트로 변환"""
    client = speech.SpeechClient()

    # 오디오 파일 설정
    with open(audio_file, 'rb') as audio:
        audio_content = audio.read()
    
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code='en-US'
    )

    # 음성 인식 요청
    response = client.recognize(config=config, audio=audio)

    # 결과 출력
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
    return response

