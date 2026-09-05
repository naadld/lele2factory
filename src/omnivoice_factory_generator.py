import os
import sys
import logging
import numpy as np
import scipy.io.wavfile as wavfile
from typing import Dict, Any, List, Optional

logger = logging.getLogger("OmniVoiceFactoryGenerator")

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POEM_ROOT = os.path.join(os.path.dirname(FACTORY_ROOT), "poem")
DEFAULT_REF_VOICE = os.path.join(POEM_ROOT, "assets", "Vegetarian Wolf.wav")

def save_tensor_as_wav(wav_tensor, output_path: str, sample_rate: int = 24000):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if hasattr(wav_tensor, "cpu"):
        audio_np = wav_tensor.cpu().numpy()
    else:
        audio_np = np.array(wav_tensor)

    audio_np = np.squeeze(audio_np).flatten()

    if audio_np.dtype != np.int16:
        max_val = np.max(np.abs(audio_np))
        if max_val > 0:
            audio_np = audio_np / max_val
        audio_np = (audio_np * 32767).clip(-32768, 32767).astype(np.int16)

    wavfile.write(output_path, sample_rate, audio_np)

class OmniVoiceFactoryGenerator:
    def __init__(self, mock_mode: bool = False, ref_voice_path: Optional[str] = None):
        self.mock_mode = mock_mode
        self.ref_voice_path = ref_voice_path or DEFAULT_REF_VOICE
        self.default_chinese_lang = "cmn"
        self.default_vietnamese_lang = "vie"
        self.model = None

    def _load_model(self):
        if self.mock_mode:
            return
        if self.model is None:
            from omnivoice import OmniVoice
            logger.info("[OMNIVOICE] Loading OmniVoice pre-trained model (k2-fsa/OmniVoice)...")
            self.model = OmniVoice.from_pretrained("k2-fsa/OmniVoice")

    def synthesize_lesson_audio(
        self,
        chinese_sentence: str,
        vietnamese_translation: str,
        output_wav_path: str
    ) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)

        if self.mock_mode or not os.path.exists(self.ref_voice_path):
            logger.info(f"[OMNIVOICE-MOCK] Generating synthetic WAV audio to: {output_wav_path}")
            sr = 24000
            duration_sec = 12.0
            t = np.linspace(0, duration_sec, int(sr * duration_sec))
            audio_data = (np.sin(2 * np.pi * 440 * t) * 16384).astype(np.int16)
            wavfile.write(output_wav_path, sr, audio_data)

            # Build synthetic timestamp cues
            words = list(chinese_sentence)
            cues = []
            cur_ms = 500
            step_ms = 400
            for idx, char in enumerate(words):
                cues.append({
                    "word": char,
                    "start_ms": cur_ms,
                    "end_ms": cur_ms + step_ms
                })
                cur_ms += step_ms

            return {
                "success": True,
                "audio_path": output_wav_path,
                "cues": cues,
                "duration_ms": int(duration_sec * 1000)
            }

        self._load_model()
        logger.info(f"[OMNIVOICE-LIVE] Synthesizing Chinese sentence: '{chinese_sentence}'")
        wav_cn = self.model.generate(text=chinese_sentence, ref_audio=self.ref_voice_path, lang_id=self.default_chinese_lang)
        
        logger.info(f"[OMNIVOICE-LIVE] Synthesizing Vietnamese translation: '{vietnamese_translation}'")
        wav_vi = self.model.generate(text=vietnamese_translation, ref_audio=self.ref_voice_path, lang_id=self.default_vietnamese_lang)

        # Concatenate audio tensors with 0.5s silence gap
        silence = np.zeros(int(24000 * 0.5), dtype=np.int16)
        cn_np = wav_cn.cpu().numpy() if hasattr(wav_cn, "cpu") else np.array(wav_cn)
        vi_np = wav_vi.cpu().numpy() if hasattr(wav_vi, "cpu") else np.array(wav_vi)

        full_audio = np.concatenate([cn_np.flatten(), silence, vi_np.flatten()])
        save_tensor_as_wav(full_audio, output_wav_path, sample_rate=24000)

        # Estimate word-level cues
        cues = []
        cn_duration_ms = int((len(cn_np.flatten()) / 24000) * 1000)
        char_count = max(1, len(chinese_sentence))
        per_char_ms = cn_duration_ms // char_count
        for idx, char in enumerate(chinese_sentence):
            cues.append({
                "word": char,
                "start_ms": idx * per_char_ms,
                "end_ms": (idx + 1) * per_char_ms
            })

        return {
            "success": True,
            "audio_path": output_wav_path,
            "cues": cues,
            "duration_ms": int((len(full_audio) / 24000) * 1000)
        }
