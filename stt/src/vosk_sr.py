from vosk import Model, KaldiRecognizer
import os
import sys
import pyaudio

# 모델 경로 확인
model_path = "C:/BLENDING/stt/src/model/vosk-model-small-ko-0.22"
if not os.path.exists(model_path):
    print("Model directory not found. Please ensure the model is unpacked in the 'model' folder.")
    exit(1)

# Vosk 모델 로드
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)

# PyAudio 설정
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
stream.start_stream()

# 음성 인식 처리
try:
    print("Listening... Say something!")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            print(rec.Result())
        else:
            # 출력 내용이 많으면, "partial" 결과를 제한적으로 출력하도록 조정할 수 있음
            partial = rec.PartialResult()
            if partial != '{"partial" : ""}':
                print(partial)

except KeyboardInterrupt:
    # 사용자가 Ctrl+C를 누르면 종료
    print("Exiting...")

finally:
    # 리소스 정리
    print("Cleaning up...")
    stream.stop_stream()
    stream.close()
    p.terminate()


