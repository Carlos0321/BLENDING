import pyaudio

class MicrophoneStream:
    def __init__(self, rate=16000, chunk_size=1024, device_index=None):
        self.rate = rate
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.audio_interface = pyaudio.PyAudio()
        self.audio_stream = None

    def __enter__(self):
        try:
            self.audio_stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,  # 추가된 부분
                frames_per_buffer=self.chunk_size
            )
        except Exception as e:
            print(f"An error occurred while opening the audio stream: {e}")
            raise e
        return self

    def __exit__(self, type, value, traceback):
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        self.audio_interface.terminate()

    def generator(self):
        try:
            while True:
                audio_chunk = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                print("Audio chunk read: ", len(audio_chunk))
                yield audio_chunk
        except GeneratorExit:
            return
        except Exception as e:
            print(f"An error occurred while reading the audio stream: {e}")
            raise e


