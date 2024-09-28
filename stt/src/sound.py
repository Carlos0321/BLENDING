import sounddevice as sd
import numpy as np
import openai
from scipy.io.wavfile import write
import tempfile
import os

# API 키 설정
openai.api_key = 'sk-proj-z24vVJW2KV6GTLE486MUT3BlbkFJIpdIuYId9qoqz37Fwe8O'

def record_audio(duration=5, fs=44100):
    """마이크로부터 오디오를 녹음하는 함수"""
    print("Recording...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float64')
    sd.wait()  # 녹음이 끝날 때까지 기다림
    print("Recording stopped.")
    return myrecording

def save_wav(file_path, data, fs):
    """녹음 데이터를 WAV 파일로 저장"""
    write(file_path, fs, data)

def transcribe_audio(file_path):
    """음성 파일을 텍스트로 변환"""
    with open(file_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    return response['text']

def main():
    fs = 44100  # 샘플 레이트
    duration = 5  # 녹음 시간(초)
    
    # 오디오 녹음
    audio_data = record_audio(duration, fs)
    
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        save_wav(temp_file.name, audio_data, fs)
        temp_file_path = temp_file.name  # 파일 경로 저장

    # 오디오 파일을 텍스트로 변환
    try:
        transcription = transcribe_audio(temp_file_path)
        print("Transcribed Text:", transcription)
    finally:
        os.remove(temp_file_path)  # 임시 파일 삭제

if __name__ == "__main__":
    main()

