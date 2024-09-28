import pyaudio
import numpy as np
import torch
import whisper
import pyttsx3
from threading import Thread
import time

class RealtimeVoiceRecognizer:
    def __init__(self, timeout=10):
        self.model = whisper.load_model("base")
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        self.engine = pyttsx3.init()
        self.timeout = timeout
        self.silence_threshold = 500  # 임계값 설정, 환경에 따라 조절 필요

    def process_audio(self):
        print("Listening... Speak now.")
        start_time = time.time()
        audio_active = False
        last_audio_time = time.time()

        while time.time() - start_time < self.timeout:
            audio_data = self.stream.read(1024, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            if np.abs(audio_array).mean() > self.silence_threshold:
                if not audio_active:
                    print("Voice detected, processing...")
                audio_active = True
                last_audio_time = time.time()

            if audio_active:
                try:
                    audio_tensor = torch.tensor(audio_array).unsqueeze(0)
                    print(f"About to transcribe, audio_tensor: {audio_tensor}")
                    result = self.model.transcribe(audio_tensor)
                    print(f"Transcription result type: {type(result)}, result: {result}")
                    
                    if isinstance(result, dict):
                        print("Result is a dictionary.")
                        transcribed_text = result.get('text', '')
                    elif isinstance(result, list) and result:
                        print("Result is a list.")
                        transcribed_text = ' '.join([item.get('text', '') for item in result if isinstance(item, dict)])
                    else:
                        print("Unknown result type.")
                        transcribed_text = ""
                    
                    self.speak(transcribed_text)
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    audio_active = False  # Reset audio_active flag after processing

            if audio_active and (time.time() - last_audio_time > 1.0):
                print("Silence detected, stopping.")
                break

    def speak(self, text):
        """Converts text to speech and outputs it."""
        if text:
            print(f"Responding: {text}")
            self.engine.say(text)
            self.engine.runAndWait()

    def start(self):
        """Starts the streaming and processing thread."""
        thread = Thread(target=self.process_audio)
        thread.start()
        return thread

    def stop(self):
        """Stops the streaming and cleans up resources."""
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()

if __name__ == "__main__":
    recognizer = RealtimeVoiceRecognizer(timeout=30)  # 30초 동안만 인식하도록 설정
    try:
        recognizer.start()
    except KeyboardInterrupt:
        recognizer.stop()








