import pyaudio
import wave
import sys
import threading
import pygame
from google.cloud import speech
from google.cloud import texttospeech
from datetime import datetime
import os

# 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Carlos/Downloads/my-project-r-1-296013-ae4d62105804.json"
# 전역 변수로 Event 객체 선언
stop_listening = threading.Event()
# 클라이언트 초기화
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

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
    with wave.open(audio_file_path, 'rb') as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code="ko-KR",
            audio_channel_count=channels,
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

        def generate_audio_chunks():
            while True:
                chunk = wf.readframes(1024)
                if not chunk:
                    break
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

        requests = generate_audio_chunks()
        responses = speech_client.streaming_recognize(streaming_config, requests)
        listen_print_loop(responses)
    choose_input_method()  # File processing completed, prompt for next action

def transcribe_from_microphone():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 1024
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Listening...")
    stop_listening = threading.Event()

    def generate_requests():
        while not stop_listening.is_set():
            yield speech.StreamingRecognizeRequest(
                audio_content=stream.read(CHUNK))


    streaming_config = speech.StreamingRecognitionConfig(
    config=speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='ko-KR',
        enable_automatic_punctuation=True),
    interim_results=True,
    single_utterance=True)

    responses = speech_client.streaming_recognize(streaming_config, generate_requests())
    listen_print_loop(responses)

    def wait_for_exit_command():
        input("Press Enter to stop listening...\n")
        stop_listening.set()

    exit_thread = threading.Thread(target=wait_for_exit_command)
    exit_thread.start()
    exit_thread.join()

    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Stopped listening.")
    choose_input_method()

def listen_print_loop(responses):
    for response in responses:
        for result in response.results:
            if result.is_final:
                transcript = result.alternatives[0].transcript
                print("Final Transcript: {}".format(transcript))
                response_text = generate_response(transcript)
                print("Response: " + response_text)
                speak(response_text)  # 응답 텍스트를 TTS로 변환하고 재생
            else:
                print("Recognition text: {}".format(result.alternatives[0].transcript))

def generate_response(transcript):
    if "현재 시간" in transcript:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"현재 시간은 {current_time}입니다."
    else:
        return "반복해서 말씀드립니다: " + transcript

def speak(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # 재생할 수 있는 오디오 파일로 저장
    with open("response.wav", "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file 'response.wav'")
    # 재생하기
    play_sound('response.wav')


def play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # 재생이 끝날 때까지 대기
choose_input_method() 

def generate_requests():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    while not stop_listening.is_set():
        data = stream.read(1024, exception_on_overflow=False)  # 오버플로우 예외 방지
        yield speech.StreamingRecognizeRequest(audio_content=data)
    stream.stop_stream()
    stream.close()
    audio.terminate()

choose_input_method()