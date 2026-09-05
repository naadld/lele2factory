import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("Gatekeeper1Auditor")

TRADITIONAL_CHARS = set("體國說學這會個門經車愛書買點誰麼後電語漢們聽開關讓幫幾邊錢號飯題視爲為樂長師筆鐘飛樣醫難機歡顏貓藍綠雞畫雙傘齒麵髮龍媽話發頭見東廣氣兒業產當實問動過進無報萬選與對總結聲變陽陰雲風魚鳥馬豬網寫讀課試檢認識記請謝賣貴賓館飲飽餓餃餅鴨鵝藥療診斷傷熱溫涼霧颱輛輪鐵銀幣帳單費稅價優質數據圖紙腦頻響錶環衛廚廳臥臺樓櫃燈鏡褲襪帶鹹鮮週遲舊圓彎遠裡處親鄰孫爺侶練護導遊員蘋傳統灣習節歲曆歷區縣鄉鎮郵園廠庫橋樹葉雜誌條隻塊張種類齊龜豐艷麗義專業務辦協參緊牽艱嘆應慶廢莊廁廂廈閃閉閏閑閔閘閣閥閱閹閻闊闌闐闔闕關韋韌韓韻頁頂頃項順須頑顧頓頗領頡頤飠飾餡餛飩饅饌饗駕駝駐駿騎騙鬆鬍鬧魂魘魯魷鮑鮫鮭鯉鯊鯨鰓鳩鳳鳴鳶鴉鴦鴛鴕鴿鴻鵑鵠鵬鶴鸚鵡鹵麥黃黨黌鈔習樂學")

ENGLISH_FORBIDDEN_WORDS = set([
    "apple", "table", "chair", "window", "book", "pencil", "school", "teacher", "student",
    "cat", "dog", "water", "rice", "food", "bus", "car", "plane", "train", "ticket",
    "hospital", "doctor", "medicine", "hotel", "room", "phone", "laptop", "computer",
    "money", "time", "day", "week", "month", "year", "today", "yesterday", "tomorrow",
    "happy", "sad", "fast", "slow", "buy", "sell", "eat", "drink", "sleep", "run", "walk"
])

def normalize_topic_string(topic: str = "") -> str:
    if not topic:
        return ""
    clean = topic.strip().lower()
    clean = re.sub(r"^(1\s*nghĩa\s*5\s*cấp|hsk\s*[1-6](-[1-6])?)\s*[•\-\:\.\/]\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"[\s\-_•\:\;\/\,\.\(\)]+", " ", clean).strip()
    return clean

def check_simplified_chinese(text: str) -> List[str]:
    violations = []
    found_trad = [c for c in text if c in TRADITIONAL_CHARS]
    if found_trad:
        unique_trad = sorted(list(set(found_trad)))
        violations.append(f"Vi phạm chữ Phồn thể: Chứa các ký tự Traditional Chinese [{', '.join(unique_trad)}]. Phải là 100% Giản thể.")
    return violations

def check_topic_uniqueness(topic: str, history: List[str]) -> List[str]:
    violations = []
    if not topic or not topic.strip():
        violations.append("Chủ đề bài học không được để trống.")
        return violations

    norm_target = normalize_topic_string(topic)
    for past in history:
        norm_past = normalize_topic_string(str(past))
        if norm_past and norm_past == norm_target:
            violations.append(f"Vi phạm Negative Context: Chủ đề '{topic}' trùng lặp với bài học cũ trong lịch sử ('{past}').")
            break
    return violations

def check_vietnamese_translation(text: str) -> List[str]:
    violations = []
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    found_eng = [w for w in words if w in ENGLISH_FORBIDDEN_WORDS]
    if found_eng:
        violations.append(f"Vi phạm Tiếng Anh trong phần dịch nghĩa: [{', '.join(found_eng)}]. Phải là 100% Tiếng Việt.")
    return violations

def audit_factory_lesson_gk1(lesson: Dict[str, Any], history: List[str] = None) -> Dict[str, Any]:
    history = history or []
    topic = lesson.get("topic", "")
    chinese_text = lesson.get("chinese_text", "")
    vietnamese_translation = lesson.get("vietnamese_translation", "")

    errors = []
    errors.extend(check_simplified_chinese(chinese_text))
    errors.extend(check_topic_uniqueness(topic, history))
    errors.extend(check_vietnamese_translation(vietnamese_translation))

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors
    }
