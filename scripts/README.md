# 🔧 Scripts — Utility & Setup Scripts

One-time setup and utility scripts.

## authenticate_gmail.py
Sets up Gmail OAuth2 credentials for email delivery features.

**Run once to authorize:**
```bash
python authenticate_gmail.py
```
This will open a browser window for Google OAuth authorization and save credentials locally.

**Requirements:**
- `credentials.json` from Google Cloud Console (Gmail API enabled)
- Python packages: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
