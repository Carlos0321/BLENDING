import whisper
import numpy as np
import torch

# Whisper 모델 로드
model = whisper.load_model("base")

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





