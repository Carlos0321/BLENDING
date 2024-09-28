import pyaudio
import wave
import os
import threading
import pygame
from openai import Audio
from datetime import datetime
import openai

# API 키 설정
openai.api_key ='sk-proj-z24vVJW2KV6GTLE486MUT3BlbkFJIpdIuYId9qoqz37Fwe8O'
# 전역 변수로 Event 객체 선언
stop_listening = threading.Event()

def record_from_microphone(filename="input.wav"):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5  # 녹음 시간 설정
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    frames = []

    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# def transcribe_audio(filename="input.wav"):
#     # 파일을 바이너리 읽기 모드로 열기
#     with open(filename, "rb") as audio_file:
#         # `file` 파라미터를 명시적으로 사용
#         response = openai.Audio.transcribe(
#             model="whisper-large",
#             file=audio_file  # 파일 객체를 직접 전달
#         )
#         transcript = response['text']
#         print("Final Transcript: {}".format(transcript))
#         return transcript
def transcribe_audio(filename="input.wav"):
    with open(filename, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",  # 현재 사용 가능한 모델로 변경
            file=audio_file
            #verbose=True  # 요청에 관한 더 많은 정보를 출력
        )
        transcript = response['data'][0]['text']  # 응답 구조에 따라 적절하게 접근
        print("Final Transcript: {}".format(transcript))
        return transcript
    
def generate_response(transcript):
    if "현재 시간" in transcript:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"현재 시간은 {current_time}입니다."
    else:
        return "반복해서 말씀드립니다: " + transcript

def speak(text):
    pygame.mixer.init()
    tts_response = Audio.create_tts(text=text, voice="korean-neutral")
    with open("response.wav", "wb") as out:
        out.write(tts_response["audio"])
    pygame.mixer.music.load("response.wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def main():
    record_from_microphone()  # 마이크로부터 녹음
    transcript = transcribe_audio()  # 음성을 텍스트로 변환
    response_text = generate_response(transcript)  # 텍스트 응답 생성
    print("Response: " + response_text)
    speak(response_text)  # 응답 텍스트를 TTS로 변환하고 재생

if __name__ == "__main__":
    main()
