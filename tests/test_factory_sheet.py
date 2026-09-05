import os
import sys
import pytest

# Add factory directory to sys.path
FACTORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY_ROOT not in sys.path:
    sys.path.insert(0, FACTORY_ROOT)

from src.gsheet_factory_manager import GSheetFactoryManager, LELE_FACTORY_COLUMNS

def test_gsheet_factory_columns_schema():
    assert len(LELE_FACTORY_COLUMNS) == 16
    assert LELE_FACTORY_COLUMNS[0] == "#"
    assert LELE_FACTORY_COLUMNS[1] == "Topic"
    assert LELE_FACTORY_COLUMNS[2] == "Level"
    assert LELE_FACTORY_COLUMNS[3] == "Status"
    assert LELE_FACTORY_COLUMNS[4] == "Word 1"
    assert LELE_FACTORY_COLUMNS[8] == "Word 5"
    assert LELE_FACTORY_COLUMNS[9] == "Metadata"
    assert LELE_FACTORY_COLUMNS[10] == "Video"
    assert LELE_FACTORY_COLUMNS[11] == "Youtube"
    assert LELE_FACTORY_COLUMNS[12] == "Tiktok"
    assert LELE_FACTORY_COLUMNS[13] == "Facebook"
    assert LELE_FACTORY_COLUMNS[14] == "Created At"
    assert LELE_FACTORY_COLUMNS[15] == "Notes"

def test_gsheet_factory_manager_init():
    mgr = GSheetFactoryManager()
    assert mgr.tab_name == "lele_factory"
    assert mgr.spreadsheet_id is not None
