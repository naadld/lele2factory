import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from scripts.run_factory_qc import inspect_factory_video_gk2

def test_gatekeeper2_video_inspection_mock():
    video_path = "/tmp/test_factory_hyperframes_render.mp4"
    res = inspect_factory_video_gk2(video_path, mock_mode=True)
    assert res["passed"] is True
    assert res["resolution"] == "1080x1920"
    assert res["fps"] == 60
