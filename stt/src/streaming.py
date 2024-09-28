import time
import pyttsx3
import openai
import numpy as np
import torch
import whisper
import logging
from mic_stream import MicrophoneStream

# 로깅 기본 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenAI API 키 설정
openai.api_key = 'sk-proj-z24vVJW2KV6GTLE486MUT3BlbkFJIpdIuYId9qoqz37Fwe8O'

# 이전 대화를 저장할 리스트 초기화
conversation_history = []

def load_model():
    try:
        logging.info("Attempting to load whisper model.")
        model = whisper.load_model("base")
        logging.info("Whisper model loaded successfully.")
        return model
    except AttributeError as e:
        logging.error(f"Failed to load model: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

def preprocess_audio(audio_chunk):
    # 오디오 데이터를 numpy 배열로 변환하고 부동 소수점으로 캐스팅하여 정규화
    audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0  # Normalize to [-1, 1]
    audio_tensor = torch.tensor(audio_array).unsqueeze(0)  # (1, num_samples) 형태로 만들기
    return audio_tensor

def decode_audio(model, audio_tensor):
    # `log_mel_spectrogram`은 (num_samples,) 또는 (batch_size, num_samples) 형태의 입력을 기대함
    if audio_tensor.dim() == 3 and audio_tensor.size(0) == 1:
        audio_tensor = audio_tensor.squeeze(0)  # (1, num_samples)로 차원 축소
    mel = whisper.log_mel_spectrogram(audio_tensor)
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)
    return result.text


def generate_response(user_text):
    # 대화 내역에 현재 대화 추가
    conversation_history.append({'role': 'user', 'content': user_text})
    
    # GPT-3.5 모델을 사용하여 응답 생성
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    
    # 응답 텍스트 반환
    return response['choices'][0]['message']['content']

def text_to_speech(text):
    # pyttsx3를 이용한 TTS 기능 구현
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    model = load_model()
    device_index = None

    with MicrophoneStream(device_index=device_index) as stream:
        print("Listening...")
        for audio_chunk in stream.generator():
            if audio_chunk is not None:
                audio_tensor = preprocess_audio(audio_chunk)
                text = decode_audio(model, audio_tensor)
                if text.strip():
                    print(f"Transcribed Text: {text}")
                    response = generate_response(text)
                    print(f"Response: {response}")
                    text_to_speech(response)
                    conversation_history.append({'role': 'user', 'content': text})
                    conversation_history.append({'role': 'assistant', 'content': response})

if __name__ == "__main__":
    main()

