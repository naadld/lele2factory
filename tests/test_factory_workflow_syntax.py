import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

def test_workflow_file_exists():
    wf_path = os.path.join(FACTORY_ROOT, ".github", "workflows", "lele_factory_render.yml")
    assert os.path.exists(wf_path), "Workflow file lele_factory_render.yml must exist"
    
    with open(wf_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "render_hyperframes_video.py" in content
        assert "run_factory_qc.py" in content
