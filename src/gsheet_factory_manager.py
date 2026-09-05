import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger("GSheetFactoryManager")

LELE_FACTORY_COLUMNS = [
    "#",
    "Topic",
    "Level",
    "Status",
    "Word 1",
    "Word 2",
    "Word 3",
    "Word 4",
    "Word 5",
    "Metadata",
    "Video",
    "Youtube",
    "Tiktok",
    "Facebook",
    "Created At",
    "Notes"
]

DEFAULT_SPREADSHEET_ID = "1b6LNl7JHRiCsjK1w9VuD86GLqAfmSOtDUOm5whrGdH0"
DEFAULT_SA_PATH = "/home/vpsg24gb/.cloud-profiles/lelehoctiengtrung/google_sa/service_account.json"

class GSheetFactoryManager:
    def __init__(self, credentials_path: Optional[str] = None, spreadsheet_id: Optional[str] = None, tab_name: str = "lele_factory"):
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID") or DEFAULT_SPREADSHEET_ID
        self.tab_name = tab_name
        self.credentials_path = credentials_path or os.getenv("GOOGLE_SA_PATH") or DEFAULT_SA_PATH
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._authenticate()

    def _get_credentials(self) -> Credentials:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        env_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON") or os.getenv("SERVICE_ACCOUNT_JSON")
        if env_json and env_json.strip():
            try:
                info = json.loads(env_json)
                return Credentials.from_service_account_info(info, scopes=scopes)
            except Exception as e:
                logger.warning(f"Failed to parse credentials from env JSON: {e}")

        if os.path.exists(self.credentials_path):
            return Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        
        raise FileNotFoundError(f"Google Service Account credentials not found at {self.credentials_path}")

    def _authenticate(self):
        try:
            creds = self._get_credentials()
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            try:
                self.worksheet = self.spreadsheet.worksheet(self.tab_name)
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"Tab '{self.tab_name}' not found. Creating tab with 16 standard columns...")
                self.worksheet = self.spreadsheet.add_worksheet(title=self.tab_name, rows="500", cols="20")
                self.init_header()
        except Exception as e:
            logger.warning(f"GSheetFactoryManager authentication warning: {e}")

    def init_header(self):
        if self.worksheet:
            self.worksheet.update('A1:P1', [LELE_FACTORY_COLUMNS])
            logger.info(f"Initialized 16 header columns for tab '{self.tab_name}'.")

    def get_all_rows(self) -> List[Dict[str, Any]]:
        if not self.worksheet:
            return []
        return self.worksheet.get_all_records()

    def update_batch_status(self, row_number: int, status: str, video_link: Optional[str] = None, notes: Optional[str] = None):
        if not self.worksheet:
            return
        self.worksheet.update(f'D{row_number}', [[status]])
        if video_link:
            self.worksheet.update(f'K{row_number}', [[video_link]])
        if notes:
            self.worksheet.update(f'P{row_number}', [[notes]])
        logger.info(f"Updated row {row_number} -> Status: '{status}'")
