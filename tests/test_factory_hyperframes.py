import os
import sys
import pytest

FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

def test_hyperframes_template_files_exist():
    template_html = os.path.join(FACTORY_ROOT, "render", "hyperframes_lesson_template.html")
    engine_js = os.path.join(FACTORY_ROOT, "render", "hyperframes_engine.js")
    
    assert os.path.exists(template_html), "Hyperframes HTML template must exist"
    assert os.path.exists(engine_js), "Hyperframes JS engine must exist"
    
    with open(template_html, "r", encoding="utf-8") as f:
        html_content = f.read()
        assert "1080" in html_content
        assert "1920" in html_content
        assert "Hyperframes" in html_content or "hyperframes" in html_content
