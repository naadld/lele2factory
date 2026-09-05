import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from scripts.render_hyperframes_video import render_hyperframes_lesson_video

def test_hyperframes_renderer_mock_execution():
    lesson_payload = {
        "title": "Khẩu ngữ: 没门儿",
        "topic": "没门儿",
        "chinese_text": "想借我的车？你可真是想得美，没门儿！",
        "pinyin": "xiǎng jiè wǒ de chē ？ nǐ kě zhēn shì xiǎng de měi ， méi ménr ！",
        "han_viet": "Hán Việt: Tưởng tá ngã đích xa...",
        "vietnamese_translation": "Muốn mượn xe của tôi á? Bạn đúng là nằm mơ giữa ban ngày, không đời nào!",
        "cues": [{"word": "想", "start_ms": 100, "end_ms": 500}]
    }
    
    output_mp4 = "/tmp/test_factory_hyperframes_render.mp4"
    res = render_hyperframes_lesson_video(lesson_payload, output_mp4, mock_mode=True)
    
    assert res["success"] is True
    assert os.path.exists(res["video_path"])
    assert res["resolution"] == "1080x1920"
    assert res["fps"] == 60
