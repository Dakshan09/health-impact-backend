"""
Gmail OAuth2 Authentication Setup Script
Run this once to authorize the application to access Gmail on your behalf.

This will:
1. Open a browser for Google sign-in
2. Request permission to send emails via Gmail API
3. Save the authorization token to token.json

Usage: python authenticate_gmail.py
"""

import os
import sys


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def authenticate():
    """Run the full OAuth2 authentication flow."""
    print("=" * 60)
    print("  Health Impact Analyzer - Gmail API Authentication")
    print("=" * 60)
    print()

    # Check for required libraries
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("❌ Missing required libraries. Please run:")
        print()
        print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print()
        sys.exit(1)

    # Check for credentials file
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ '{CREDENTIALS_FILE}' not found in the current directory.")
        print()
        print("To fix this:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create or select a project")
        print("  3. Enable the Gmail API and Google Sheets API")
        print("  4. Create OAuth2 Desktop credentials")
        print("  5. Download as 'credentials.json' and place it here")
        print()
        sys.exit(1)

    creds = None

    # Try to load existing token
    if os.path.exists(TOKEN_FILE):
        print(f"📋 Found existing token: {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds and creds.valid:
                print("✅ Existing token is valid. No re-authentication needed.")
                _test_connection(creds)
                return creds
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Token expired. Refreshing...")
                creds.refresh(Request())
                _save_token(creds)
                print("✅ Token refreshed successfully.")
                _test_connection(creds)
                return creds
        except Exception as e:
            print(f"⚠️  Existing token invalid ({e}). Re-authenticating...")
            creds = None

    # Run fresh authentication flow
    print()
    print("🌐 Starting OAuth2 authentication...")
    print("   A browser window will open for you to sign in to Google.")
    print("   Please allow the requested permissions.")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(
            port=0,
            success_message="Authentication complete! You can close this window.",
            open_browser=True,
        )
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("If the browser did not open, try running:")
        print("   python authenticate_gmail.py --no-browser")
        sys.exit(1)

    # Save the token
    _save_token(creds)

    print()
    print("✅ Authentication successful!")
    print(f"   Token saved to: {TOKEN_FILE}")
    print()

    _test_connection(creds)
    return creds


def _save_token(creds):
    """Save credentials to token.json."""
    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(creds.to_json())


def _test_connection(creds):
    """Test the Gmail connection by checking profile."""
    try:
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress", "unknown")
        print(f"📧 Authenticated as: {email}")
        print()
        print("Gmail API is ready to send health reports!")
        print()
        print("Next steps:")
        print("  1. Add GOOGLE_SHEET_ID to your .env file (optional, for data logging)")
        print("  2. Run the main system: python main.py")
        print("  3. Test email delivery: python tools/communication/email_delivery.py your@email.com")
    except Exception as e:
        print(f"⚠️  Could not verify connection: {e}")


if __name__ == "__main__":
    # Handle --no-browser flag for headless environments
    if "--no-browser" in sys.argv:
        print("⚠️  --no-browser mode not supported with run_local_server.")
        print("    Please run without the flag on a machine with a browser.")
        sys.exit(1)

    # Change to script directory so credential files are found
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    authenticate()
