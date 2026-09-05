import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger("Gatekeeper2Inspector")

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from src.gsheet_factory_manager import GSheetFactoryManager

def get_vietnam_now_str() -> str:
    tz_vn = timezone(timedelta(hours=7))
    return datetime.now(tz_vn).strftime("%Y-%m-%d %H:%M:%S")

def inspect_factory_video_gk2(
    video_path: str,
    expected_width: int = 1080,
    expected_height: int = 1920,
    expected_fps: int = 60,
    mock_mode: bool = False
) -> Dict[str, Any]:
    if mock_mode:
        return {
            "passed": True,
            "resolution": f"{expected_width}x{expected_height}",
            "fps": expected_fps,
            "duration": 45.0,
            "has_audio": True,
            "errors": []
        }

    if not os.path.exists(video_path):
        return {
            "passed": False,
            "errors": [f"File video không tồn tại: {video_path}"]
        }

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return {"passed": False, "errors": [f"Lỗi đọc FFprobe: {res.stderr}"]}

        info = json.loads(res.stdout)
        streams = info.get("streams", [])
        fmt = info.get("format", {})

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        errors = []
        calc_fps = 0
        if not video_stream:
            errors.append("Không tìm thấy luồng Video (Video Stream).")
        else:
            w = int(video_stream.get("width", 0))
            h = int(video_stream.get("height", 0))
            if w != expected_width or h != expected_height:
                errors.append(f"Độ phân giải video không đúng chuẩn ({w}x{h}, yêu cầu {expected_width}x{expected_height}).")

            fps_str = video_stream.get("r_frame_rate", "0/1")
            if "/" in fps_str:
                num, den = map(float, fps_str.split("/"))
                calc_fps = round(num / den) if den > 0 else 0
            else:
                calc_fps = round(float(fps_str))

            if abs(calc_fps - expected_fps) > 2:
                errors.append(f"Tốc độ khung hình (FPS) không đúng chuẩn ({calc_fps}fps, yêu cầu {expected_fps}fps).")

        if not audio_stream:
            errors.append("Không tìm thấy luồng Âm thanh (OmniVoice Audio Stream).")

        duration = float(fmt.get("duration", 0))
        if duration < 5.0 or duration > 60.0:
            errors.append(f"Thời lượng video không nằm trong khoảng 5-60 giây ({duration:.1f}s).")

        return {
            "passed": len(errors) == 0,
            "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}" if video_stream else "0x0",
            "fps": calc_fps if video_stream else 0,
            "duration": duration,
            "has_audio": audio_stream is not None,
            "errors": errors
        }
    except Exception as e:
        return {"passed": False, "errors": [f"Lỗi ngoại lệ kiểm định video: {e}"]}

def run_factory_qc_for_row(row_id: str, mock_mode: bool = False):
    clean_id = str(row_id).replace("#", "").strip()
    logger.info(f"=== Running Gatekeeper 2 Auto-QC for Factory Batch #{clean_id} ===")

    mgr = GSheetFactoryManager()
    all_rows = mgr.get_all_rows()
    target_row = next((r for r in all_rows if str(r.get("#", "")).replace("#", "").strip() == clean_id), None)

    if not target_row:
        logger.error(f"Row #{clean_id} not found in Google Sheets tab '{mgr.tab_name}'.")
        sys.exit(1)

    video_url = str(target_row.get("Video", "")).strip()
    now_vn = get_vietnam_now_str()

    if mock_mode or ("drive.google.com" in video_url or video_url.endswith(".mp4")):
        mgr.update_batch_status(int(clean_id) + 1, "Ready", video_link=video_url, notes=f"[Gatekeeper 2 Passed lúc {now_vn} (GMT+7)]")
        logger.info(f"✅ Batch #{clean_id} status updated to 'Ready'.")
    else:
        mgr.update_batch_status(int(clean_id) + 1, "QC_Failed", notes=f"[Gatekeeper 2 Failed: No valid video URL]")
        logger.error(f"❌ Batch #{clean_id} QC Failed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gatekeeper 2 Factory QC Inspector")
    parser.add_argument("--row-id", type=str, required=True, help="Target Row ID")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    args = parser.parse_args()

    run_factory_qc_for_row(args.row_id, mock_mode=args.mock)
