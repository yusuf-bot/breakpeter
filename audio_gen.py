import os
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS

device = "cpu"  # or "cuda" if available

# Preload models globally so we don't reload every time
ckpt_converter = "checkpoints_v2/converter"
tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
se_extractor.device='cpu'
def clone_voice_openvoice(clone_audio_path, text, output_path):
    try:
        # Step 1: Extract speaker embedding
        target_se, audio_name = se_extractor.get_se(clone_audio_path, tone_color_converter, vad=False)

        # Step 2: Generate temp voice audio from text
        temp_tts_path = os.path.join(os.path.dirname(output_path), "tmp.wav")
        lang = "EN"
        speed = 1.0
        model = TTS(language=lang, device=device)
        speaker_ids = model.hps.data.spk2id

        # Pick any valid speaker
        speaker_key = list(speaker_ids.keys())[0]
        speaker_id = speaker_ids[speaker_key]
        speaker_key = speaker_key.lower().replace("_", "-")
        source_se = torch.load(f'checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=device)

        model.tts_to_file(text, speaker_id, temp_tts_path, speed=speed)

        # Step 3: Convert to cloned voice
        tone_color_converter.convert(
            audio_src_path=temp_tts_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path
        )

        return output_path
    except Exception as e:
        print(f"❌ OpenVoice Error: {e}")
        return None

