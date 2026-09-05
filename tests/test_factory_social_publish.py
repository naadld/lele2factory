import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from scripts.publish_factory_social import publish_factory_row_to_social

def test_factory_social_publish_dry_run():
    res = publish_factory_row_to_social(
        row_id=2,
        channels="all",
        dry_run=True,
        target_vn_str="11:00 05/09"
    )
    assert res["status"] == "success"
    assert res["row_id"] == 2
    assert "dispatched" in res
    assert len(res["dispatched"]) > 0
