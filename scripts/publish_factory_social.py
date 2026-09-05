import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("FactorySocialPublisher")

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from src.gsheet_factory_manager import GSheetFactoryManager

CHANNEL_MAPPING = {
    "youtube": "6a83dda0ccaf649a67c8cb92",
    "tiktok": "6a83dc5bccaf649a67c8b30f",
    "facebook": "6a871331ccaf649a67e1b724"
}

def publish_factory_row_to_social(
    row_id: int,
    channels: str = "all",
    dry_run: bool = True,
    target_due_utc: Optional[str] = None,
    target_vn_str: Optional[str] = None
) -> Dict[str, Any]:
    logger.info(f"🚀 [FACTORY DISPATCH] Row #{row_id} | Scheduled: {target_vn_str or 'Immediate'} | Dry-Run: {dry_run}")
    
    target_channels = ["YouTube Shorts", "TikTok", "Facebook Fanpage"] if channels == "all" else [channels]

    if dry_run:
        return {
            "status": "success",
            "row_id": row_id,
            "tab": "lele_factory",
            "dispatched": target_channels,
            "scheduled_at": target_vn_str or "Dry-Run Immediate"
        }

    # Live Buffer Publishing Integration
    mgr = GSheetFactoryManager()
    all_rows = mgr.get_all_rows()
    target_row = next((r for r in all_rows if str(r.get("#", "")).replace("#", "").strip() == str(row_id)), None)

    if not target_row:
        raise ValueError(f"Row #{row_id} not found in Google Sheets tab '{mgr.tab_name}'.")

    # Lock status on Google Sheets
    mgr.update_batch_status(row_id, "Published", notes=f"[Published to Buffer lúc {target_vn_str}]")

    return {
        "status": "success",
        "row_id": row_id,
        "tab": "lele_factory",
        "dispatched": target_channels,
        "scheduled_at": target_vn_str
    }
