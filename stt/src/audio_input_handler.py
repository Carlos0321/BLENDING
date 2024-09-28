import librosa  # for audio processing
import soundfile as sf

def convert_to_wav(file_path):
    """Convert an audio file to WAV format using soundfile library."""
    audio_data, sample_rate = librosa.load(file_path, sr=None)
    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
    sf.write(wav_path, audio_data, sample_rate)
    return wav_path
