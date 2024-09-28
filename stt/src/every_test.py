import os

model_path = "C:/BLENDING/stt/src/model/vosk-model-small-ko-0.22"
  # 상대 경로 또는 절대 경로로 변경
full_path = os.path.abspath(model_path)
print("Looking for model in:", full_path)

if not os.path.exists(full_path):
    print("Model directory not found.")
    exit(1)
