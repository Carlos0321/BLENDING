import os
import wave
import pyaudio
from google.cloud import speech_v1p1beta1 as speech

# Google Cloud Speech-to-Text API 인증 파일 경로 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/Carlos/Downloads/my-project-r-1-296013-ae4d62105804.json"

# Speech-to-Text 클라이언트 생성
client = speech.SpeechClient()

def transcribe_from_microphone():
    # mic 설정
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("듣는 중...")

    # 스트리밍 인식 설정
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="ko-KR",
        audio_channel_count=CHANNELS,
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    # 오디오 스트림에서 데이터를 읽어오는 제너레이터 함수
    def generate_audio_chunks():
        while True:
            chunk = stream.read(CHUNK, exception_on_overflow=False)
            if not chunk:
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    requests = generate_audio_chunks()
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            if result.is_final:
                print("Final Transcript: {}".format(result.alternatives[0].transcript))
            else:
                print("Partial transcript: {}".format(result.alternatives[0].transcript))

    stream.stop_stream()
    stream.close()
    audio.terminate()

def transcribe_from_file(audio_file_path):
    # WAV 파일 열기
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
        responses = client.streaming_recognize(streaming_config, requests)

        for response in responses:
            for result in response.results:
                if result.is_final:
                    print("Transcript: {}".format(result.alternatives[0].transcript))
                else:
                    print("Partial transcript: {}".format(result.alternatives[0].transcript))

def main():
    mode = input("Choose input mode (1: Microphone, 2: Audio File): ")
    if mode == "1":
        transcribe_from_microphone()
    elif mode == "2":
        audio_file_path = input("Enter the path to the audio file: ")
        transcribe_from_file(audio_file_path)
    else:
        print("Invalid input. Please enter 1 or 2.")

if __name__ == "__main__":
    main()



