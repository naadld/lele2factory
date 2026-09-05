import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from src.omnivoice_factory_generator import OmniVoiceFactoryGenerator

def test_omnivoice_factory_generator_init():
    gen = OmniVoiceFactoryGenerator()
    assert gen.default_chinese_lang == "cmn"
    assert gen.default_vietnamese_lang == "vie"

def test_omnivoice_lesson_speech_builder_mock():
    gen = OmniVoiceFactoryGenerator(mock_mode=True)
    res = gen.synthesize_lesson_audio(
        chinese_sentence="想借我的车？你可真是想得美，没门儿！",
        vietnamese_translation="Muốn mượn xe của tôi á? Bạn đúng là nằm mơ giữa ban ngày, không đời nào!",
        output_wav_path="/tmp/test_factory_lesson.wav"
    )
    assert res["success"] is True
    assert os.path.exists(res["audio_path"])
    assert len(res["cues"]) > 0
    assert "start_ms" in res["cues"][0]
