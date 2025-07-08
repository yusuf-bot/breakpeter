import os
import time
from TTS.api import TTS
from pydub import AudioSegment  # Optional: to save as MP3


def clone_voice_coqui(audio_path, text_to_speak, output_path="cloned_voice.wav", language="en"):
    print("🧠 Loading Coqui TTS model...")
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=True, gpu=False)

    print("🔊 Generating speech with voice cloning...")
    tts.tts_to_file(
        text=text_to_speak,
        speaker_wav=audio_path,
        language=language,
        file_path=output_path
    )

    print(f"✅ Cloned voice saved as: {output_path}")


def convert_to_mp3(wav_path, mp3_path):
    """Optional: Convert WAV to MP3 using pydub."""
    sound = AudioSegment.from_wav(wav_path)
    sound.export(mp3_path, format="mp3")
    print(f"🎵 Converted to MP3: {mp3_path}")


# === Example usage ===
if __name__ == "__main__":
    speaker_audio = "peter_clone.wav"  # Path to your speaker sample (already cloned)
    text = ("Oh, yeah, we've made deals with the UK and Vietnam. "
            "Vietnam's getting a lower tariff than what Trump first threatened. "
            "It's like haggling at a yard sale, but with countries. And the UK, well, "
            "they're just happy to be getting any deal after that Brexit mess. It's like they're "
            "the kid that's just happy to be invited to the party, you know?")

    wav_output = "cloned_output.wav"
    mp3_output = "cloned_output.mp3"

    clone_voice_coqui(speaker_audio, text, wav_output)
    convert_to_mp3(wav_output, mp3_output)
