"""
Google Sheets Data Logger
Logs patient health data and reports to a Google Sheet for tracking.
"""

import os
import json
from datetime import datetime
from typing import Optional


def _get_sheets_service():
    """Initialize and return the Google Sheets API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Google API libraries not installed. Run: pip install google-auth google-api-python-client"
        )

    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Google Sheets not authenticated. Run authenticate_gmail.py first."
            )

    service = build("sheets", "v4", credentials=creds)
    return service


def log_data(data: dict, spreadsheet_id: Optional[str] = None) -> bool:
    """
    Log patient health data to Google Sheets.

    Args:
        data: Patient data dictionary
        spreadsheet_id: Google Sheets ID (from GOOGLE_SHEET_ID env var if None)

    Returns:
        True if logged successfully, False otherwise
    """
    sheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEET_ID")

    patient_name = data.get("fullName", "Anonymous")
    print(f"Logging data to Google Sheets for: {patient_name}")

    if not sheet_id:
        _log_to_local_file(data)
        print("[WARN] GOOGLE_SHEET_ID not set. Data logged to local file instead.")
        return False

    try:
        service = _get_sheets_service()

        # Prepare row data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            data.get("fullName", ""),
            data.get("age", ""),
            data.get("gender", ""),
            data.get("email", ""),
            data.get("phone", ""),
            ", ".join(data.get("conditions", [])),
            data.get("medications", ""),
            data.get("smokingStatus", ""),
            data.get("alcoholConsumption", ""),
            data.get("exerciseFrequency", ""),
            data.get("dietQuality", ""),
            data.get("sleepHours", ""),
            data.get("stressLevel", ""),
            data.get("currentSymptoms", ""),
            data.get("concerns", ""),
        ]

        body = {"values": [row]}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()

        print(f"[OK] Data logged to Google Sheets for {patient_name}")
        return True

    except RuntimeError as e:
        print(f"[WARN] Google Sheets not configured: {e}")
        _log_to_local_file(data)
        return False
    except Exception as e:
        print(f"[ERROR] Failed to log to Google Sheets: {e}")
        _log_to_local_file(data)
        return False


def _log_to_local_file(data: dict):
    """Fallback: log data to local JSON file."""
    log_dir = os.path.join(os.getcwd(), ".tmp", "cleaned_data")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in data.get("fullName", "unknown"))
    log_file = os.path.join(log_dir, f"patient_{safe_name}_{timestamp}.json")

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({**data, "_logged_at": timestamp}, f, indent=2)

    print(f"[DATA] Data saved locally: {log_file}")


def create_sheet_headers(spreadsheet_id: str) -> bool:
    """
    Initialize headers in the Google Sheet.
    Call this once when setting up a new sheet.
    """
    headers = [
        ["Timestamp", "Full Name", "Age", "Gender", "Email", "Phone",
         "Conditions", "Medications", "Smoking", "Alcohol", "Exercise",
         "Diet Quality", "Sleep Hours", "Stress Level", "Symptoms", "Concerns"]
    ]

    try:
        service = _get_sheets_service()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body={"values": headers},
        ).execute()
        print("[OK] Google Sheet headers initialized.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to set headers: {e}")
        return False


if __name__ == "__main__":
    # Demo logging
    sample_data = {
        "fullName": "Demo Patient",
        "age": "45",
        "gender": "Male",
        "email": "demo@example.com",
        "smokingStatus": "Never",
        "exerciseFrequency": "3x per week",
        "dietQuality": "Good",
        "sleepHours": "7",
        "stressLevel": "Moderate",
        "conditions": ["Hypertension"],
        "currentSymptoms": "Occasional headaches",
    }
    log_data(sample_data)
