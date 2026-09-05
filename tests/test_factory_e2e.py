import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from src.gsheet_factory_manager import LELE_FACTORY_COLUMNS
from src.omnivoice_factory_generator import OmniVoiceFactoryGenerator
from scripts.render_hyperframes_video import render_hyperframes_lesson_video
from scripts.gatekeeper1_auditor import audit_factory_lesson_gk1
from scripts.run_factory_qc import inspect_factory_video_gk2
from scripts.publish_factory_social import publish_factory_row_to_social

def test_full_factory_pipeline_e2e():
    # 1. Lesson Payload Creation
    lesson = {
        "title": "Khẩu ngữ: 没门儿",
        "topic": "没门儿",
        "chinese_text": "想借我的车？你可真是想得美，没门儿！",
        "pinyin": "xiǎng jiè wǒ de chē ？ nǐ kě zhēn shì xiǎng de měi ， méi ménr ！",
        "han_viet": "Hán Việt: Tưởng tá ngã đích xa...",
        "vietnamese_translation": "Muốn mượn xe tôi á? Bạn đúng là nằm mơ giữa ban ngày, không đời nào!"
    }
    
    # 2. Gatekeeper 1 Audit
    gk1_res = audit_factory_lesson_gk1(lesson, history=["给力", "破防"])
    assert gk1_res["passed"] is True, f"GK1 failed: {gk1_res['errors']}"
    
    # 3. OmniVoice Audio Generation (Mock Mode)
    tts_gen = OmniVoiceFactoryGenerator(mock_mode=True)
    wav_res = tts_gen.synthesize_lesson_audio(
        lesson["chinese_text"],
        lesson["vietnamese_translation"],
        "/tmp/e2e_factory_lesson.wav"
    )
    assert wav_res["success"] is True
    lesson["cues"] = wav_res["cues"]
    
    # 4. Hyperframes 60fps Video Render (Mock Mode)
    output_mp4 = "/tmp/e2e_factory_lesson_render.mp4"
    video_res = render_hyperframes_lesson_video(lesson, output_mp4, mock_mode=True)
    assert video_res["success"] is True
    assert video_res["resolution"] == "1080x1920"
    assert video_res["fps"] == 60
    
    # 5. Gatekeeper 2 Auto-QC Inspection
    gk2_res = inspect_factory_video_gk2(output_mp4, mock_mode=True)
    assert gk2_res["passed"] is True
    
    # 6. Buffer Social Dispatch (Dry-Run)
    social_res = publish_factory_row_to_social(row_id=2, channels="all", dry_run=True, target_vn_str="11:00 05/09")
    assert social_res["status"] == "success"
    assert len(social_res["dispatched"]) == 3
