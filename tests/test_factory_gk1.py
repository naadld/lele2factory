import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from scripts.gatekeeper1_auditor import audit_factory_lesson_gk1

def test_gatekeeper1_valid_lesson():
    lesson = {
        "topic": "破防",
        "chinese_text": "听到这句话我直接破防了",
        "pinyin": "tīng dào zhè jù huà wǒ zhí jiē pò fáng le",
        "vietnamese_translation": "Nghe thấy câu này tôi cảm động phát khóc"
    }
    history = ["没门儿", "给力"]
    res = audit_factory_lesson_gk1(lesson, history)
    assert res["passed"] is True
    assert len(res["errors"]) == 0

def test_gatekeeper1_duplicate_topic_rejection():
    lesson = {
        "topic": "没门儿",
        "chinese_text": "想借我的车？没门儿！",
        "pinyin": "xiǎng jiè wǒ de chē ？ méi ménr ！",
        "vietnamese_translation": "Muốn mượn xe tôi á? Không đời nào!"
    }
    history = ["1 Nghĩa 5 Cấp • 没门儿", "给力"]
    res = audit_factory_lesson_gk1(lesson, history)
    assert res["passed"] is False
    assert any("trùng lặp" in e.lower() or "duplicate" in e.lower() for e in res["errors"])

def test_gatekeeper1_traditional_chinese_rejection():
    lesson = {
        "topic": "學習",
        "chinese_text": "我要學習中文", # 學習 contains Traditional characters 簡/繁
        "pinyin": "wǒ yào xué xí zhōng wén",
        "vietnamese_translation": "Tôi muốn học tiếng Trung"
    }
    history = []
    res = audit_factory_lesson_gk1(lesson, history)
    assert res["passed"] is False
    assert any("phồn thể" in e.lower() or "traditional" in e.lower() for e in res["errors"])
