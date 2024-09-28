import pyaudio
import wave
import sys
import threading
from google.cloud import speech
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Carlos/Downloads/my-project-r-1-296013-ae4d62105804.json"
speech_client = speech.SpeechClient()

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
        interim_results=True)

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
                print("Final Transcript: {}".format(result.alternatives[0].transcript))
            else:
                print("Recognition  text: {}".format(result.alternatives[0].transcript))

choose_input_method()






