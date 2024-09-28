import pyaudio
import wave
import sys
import threading
import openai
import pyttsx3
from datetime import datetime
import os

# OpenAI API 키 설정
openai.api_key = "sk-proj-z24vVJW2KV6GTLE486MUT3BlbkFJIpdIuYId9qoqz37Fwe8O"

# 전역 변수로 Event 객체 선언
stop_listening = threading.Event()
complete_transcript = ""  # 모든 인식된 텍스트를 저장하기 위한 전역 변수

def choose_input_method():
    print("Choose input method:\n1: Microphone\n2: Audio File\n3: Exit")
    choice = input("Enter your choice (1, 2, or 3): ")
    if choice == '1':
        transcribe_from_microphone()
    elif choice == '2':
        audio_file_path = input("Enter the path to the audio file: ")
        transcribe_from_file(audio_file_path)
    elif choice == '3':
        print("Exiting the program.")
        sys.exit(0)
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        choose_input_method()

def transcribe_from_file(audio_file_path):
    global complete_transcript  # 전역 변수로 선언
    with open(audio_file_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        transcript = response["text"]
        complete_transcript += transcript  # 변환된 텍스트를 누적 저장
        print("Transcript: {}".format(transcript))
        response_text = generate_response(transcript)
        print("Response: " + response_text)
        speak(response_text)
    
    choose_input_method()

def transcribe_from_microphone():
    global complete_transcript  # 전역 변수로 선언
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    audio = pyaudio.PyAudio()

    # 마이크 스트림 열기
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Listening...")

    def listen_and_transcribe():
        global complete_transcript  # 전역 변수로 선언
        frames = []
        buffer_seconds = 2  # 최소 2초 동안 버퍼링
        buffer_chunks = int(RATE / CHUNK * buffer_seconds)
        
        while not stop_listening.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            # 오디오 데이터가 충분히 수집되었는지 확인 (최소 2초 이상)
            if len(frames) >= buffer_chunks:
                with wave.open("temp.wav", "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                frames = []

                with open("temp.wav", "rb") as audio_file:
                    try:
                        response = openai.Audio.transcribe(
                            model="whisper-1",
                            file=audio_file
                        )
                        transcript = response["text"]
                        complete_transcript += transcript  # 변환된 텍스트를 누적 저장
                        print("Intermediate Transcript: {}".format(transcript))
                        response_text = generate_response(transcript)
                        print("Response: " + response_text)
                        speak(response_text)
                    except openai.error.InvalidRequestError as e:
                        print(f"Error: {e}")
                        continue

    listen_thread = threading.Thread(target=listen_and_transcribe)
    listen_thread.start()

    def wait_for_exit_command():
        input("Press Enter to stop listening...\n")
        stop_listening.set()

    wait_for_exit_command()

    listen_thread.join()
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Final Transcript: {}".format(complete_transcript))
    choose_input_method()

def generate_response(transcript):
    if "현재 시간" in transcript:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"현재 시간은 {current_time}입니다."
    else:
        return "반복해서 말씀드립니다: " + transcript

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()

choose_input_method()













