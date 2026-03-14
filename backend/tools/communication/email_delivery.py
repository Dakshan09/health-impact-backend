"""
Email Delivery — SMTP with File Attachments
Sends health reports via SMTP (Gmail App Password or any SMTP provider).

Configuration (in .env):
    SMTP_HOST     = smtp.gmail.com
    SMTP_PORT     = 587
    SMTP_EMAIL    = your_email@gmail.com
    SMTP_PASSWORD = your_app_password   (Gmail: Settings -> Security -> App Passwords)

Gmail setup:
    1. Enable 2-Factor Authentication on your Google account
    2. Go to https://myaccount.google.com/apppasswords
    3. Generate an App Password for "Mail"
    4. Use that 16-character password as SMTP_PASSWORD
"""

import os
import smtplib
import base64
import traceback
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

# Force load .env from the backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(env_path)


def send_reports_email(
    to_address: str,
    patient_name: str,
    analysis_summary: str,
    overall_risk: str,
    attachments: list[str],  # list of absolute file paths
) -> bool:
    """
    Send health reports email with file attachments via SMTP.

    Args:
        to_address: Recipient email address (patient's email)
        patient_name: Patient's full name for personalization
        analysis_summary: Short AI analysis summary for the email body
        overall_risk: Overall risk level (High/Moderate/Low)
        attachments: List of absolute paths to files to attach

    Returns:
        True if sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_email or not smtp_password:
        print("SMTP credentials not configured (SMTP_EMAIL / SMTP_PASSWORD missing)")
        print(f"Would have sent reports to: {to_address}")
        return False

    subject = f"Your Health Impact Analysis Report -- {patient_name}"

    # Build the HTML email body
    risk_color = {"High": "#ef4444", "Moderate": "#f59e0b", "Low": "#22c55e"}.get(
        overall_risk, "#6b7280"
    )
    html_body = _build_email_html(patient_name, analysis_summary, overall_risk, risk_color)

    # Create the multipart message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"Health Impact Analyzer <{smtp_email}>"
    msg["To"] = to_address

    # Attach HTML body
    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(_build_email_plain(patient_name, overall_risk), "plain"))
    body_part.attach(MIMEText(html_body, "html"))
    msg.attach(body_part)

    # Attach report files
    for file_path in attachments:
        if not file_path or not os.path.exists(file_path):
            print(f"Attachment not found, skipping: {file_path}")
            continue
        _attach_file(msg, file_path)

    # Try STARTTLS (port 587) first, then fall back to SSL (port 465)
    last_error = None
    for method in ["starttls", "ssl"]:
        try:
            if method == "starttls":
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_email, smtp_password)
                    server.sendmail(smtp_email, [to_address], msg.as_string())
            else:
                with smtplib.SMTP_SSL(smtp_host, 465, timeout=15) as server:
                    server.login(smtp_email, smtp_password)
                    server.sendmail(smtp_email, [to_address], msg.as_string())
            print(f"SUCCESS: Email sent to {to_address} via {method} with {len(attachments)} attachment(s)")
            return True
        except OSError as e:
            last_error = e
            print(f"WARN: SMTP {method} failed with OSError: {e} -- trying next method...")
            continue
        except smtplib.SMTPAuthenticationError:
            print("FAILED: SMTP Authentication failed. Check SMTP_EMAIL and SMTP_PASSWORD.")
            traceback.print_exc()
            return False
        except Exception as e:
            last_error = e
            print(f"WARN: SMTP {method} failed: {e} -- trying next method...")
            continue

    print(f"FAILED: All SMTP methods failed. Last error: {last_error}")
    return False


def _attach_file(msg: MIMEMultipart, file_path: str):
    """Attach a file to the email message."""
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    main_type, sub_type = mime_type.split("/", 1)

    with open(file_path, "rb") as f:
        file_data = f.read()

    part = MIMEBase(main_type, sub_type)
    part.set_payload(file_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(part)
    print(f"   Attachment added: {filename} ({len(file_data) // 1024} KB)")


def _build_email_plain(patient_name: str, overall_risk: str) -> str:
    """Plain text fallback for email body."""
    return f"""Dear {patient_name},

Your Health Impact Analysis Report is ready.

Overall Risk Level: {overall_risk}

Please find your personalized health reports attached to this email:
  1. Clinical Report (PDF) -- Detailed AI-powered health analysis
  2. Visualization Report (PDF/HTML) -- Risk charts and lifestyle scores
  3. 90-Day Intervention Schedule (Excel) -- Your personalized action plan

IMPORTANT: These reports are for informational purposes only and do not 
constitute medical advice. Please consult a qualified healthcare provider 
for a proper diagnosis and treatment plan.

Generated by Health Impact Analyzer on {datetime.now().strftime("%B %d, %Y")}
"""


def _build_email_html(
    patient_name: str,
    analysis_summary: str,
    overall_risk: str,
    risk_color: str,
) -> str:
    """Rich HTML email body with styling."""
    # Truncate analysis summary for email body
    summary_preview = ""
    if analysis_summary:
        lines = [l.strip() for l in analysis_summary.split("\n") if l.strip() and not l.strip().startswith("#")]
        summary_preview = " ".join(lines[:4])[:500]
        if len(summary_preview) == 500:
            summary_preview += "..."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your Health Impact Report</title>
</head>
<body style="margin:0;padding:0;background:#f0fdf4;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08);">

  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#1a6b3c 0%,#2e8b57 100%);padding:32px 36px;">
    <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">Health Impact Analysis Report</h1>
    <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:14px;">
      Prepared for <strong>{patient_name}</strong> &nbsp;&middot;&nbsp; {datetime.now().strftime("%B %d, %Y")}
    </p>
  </td></tr>

  <!-- Risk Badge -->
  <tr><td style="padding:24px 36px 0;">
    <div style="display:inline-block;background:{risk_color}15;border:2px solid {risk_color};
                border-radius:99px;padding:8px 24px;font-weight:700;color:{risk_color};font-size:15px;">
      Overall Risk: {overall_risk}
    </div>
  </td></tr>

  <!-- Greeting -->
  <tr><td style="padding:20px 36px;">
    <p style="margin:0 0 12px;color:#374151;font-size:15px;line-height:1.6;">
      Dear <strong>{patient_name}</strong>,
    </p>
    <p style="margin:0 0 12px;color:#6b7280;font-size:14px;line-height:1.7;">
      Your personalized health impact analysis is complete. Based on the information you provided,
      our AI system has generated three comprehensive reports attached to this email.
    </p>
    {f'<p style="margin:0;color:#374151;font-size:14px;line-height:1.7;background:#f8fafc;border-left:3px solid #2e8b57;padding:12px 16px;border-radius:0 8px 8px 0;"><em>{summary_preview}</em></p>' if summary_preview else ''}
  </td></tr>

  <!-- Attachments -->
  <tr><td style="padding:0 36px 20px;">
    <h2 style="color:#1a6b3c;font-size:16px;margin:0 0 12px;font-weight:600;">Your Attached Reports</h2>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:10px 14px;background:#f0fdf4;border-radius:8px;margin-bottom:8px;border:1px solid #d1fae5;">
        <strong style="color:#1a6b3c;font-size:14px;">Clinical Report (PDF)</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Full medical analysis with risk tables and AI recommendations</p>
      </td></tr>
      <tr><td style="padding:6px 0;"></td></tr>
      <tr><td style="padding:10px 14px;background:#faf5ff;border-radius:8px;margin-bottom:8px;border:1px solid #e9d5ff;">
        <strong style="color:#7c3aed;font-size:14px;">Visualization Report (PDF/HTML)</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Color-coded risk charts and lifestyle quality scores</p>
      </td></tr>
      <tr><td style="padding:6px 0;"></td></tr>
      <tr><td style="padding:10px 14px;background:#f0fdf4;border-radius:8px;border:1px solid #d1fae5;">
        <strong style="color:#059669;font-size:14px;">90-Day Intervention Schedule (Excel)</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Personalized daily habits, milestones and weekly goals</p>
      </td></tr>
    </table>
  </td></tr>

  <!-- Next Steps -->
  <tr><td style="padding:0 36px 20px;">
    <h2 style="color:#1a6b3c;font-size:16px;margin:0 0 12px;font-weight:600;">Recommended Next Steps</h2>
    <ul style="margin:0;padding:0 0 0 18px;color:#6b7280;font-size:14px;line-height:1.8;">
      <li>Schedule a consultation with your primary care physician</li>
      <li>Share the Clinical Report PDF with your doctor</li>
      <li>Start your 90-Day Intervention Schedule</li>
      <li>Follow up in 30 days to track progress</li>
    </ul>
  </td></tr>

  <!-- Disclaimer -->
  <tr><td style="padding:16px 36px;background:#fef9c3;border-top:1px solid #fde047;">
    <p style="margin:0;color:#854d0e;font-size:12px;line-height:1.6;">
      <strong>Medical Disclaimer:</strong> These reports are generated by an AI system for informational 
      purposes only and do not constitute medical advice. Always consult a qualified healthcare professional 
      for diagnosis and treatment decisions.
    </p>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:20px 36px;text-align:center;">
    <p style="margin:0;color:#9ca3af;font-size:11px;">
      Generated by <strong>Health Impact Analyzer</strong> &nbsp;&middot;&nbsp;
      {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# --- Backward-compat simple send (no attachments) ---

def send_email(
    to_address: str,
    report_content: str,
    subject: str = None,
    patient_name: str = None,
) -> bool:
    """
    Legacy simple email sender (no attachments).
    Used by old test code. Prefers SMTP.
    """
    if not subject:
        name = patient_name or "Patient"
        subject = f"Health Impact Analysis Report - {name}"

    return send_reports_email(
        to_address=to_address,
        patient_name=patient_name or "Patient",
        analysis_summary=report_content[:200],
        overall_risk="",
        attachments=[],
    )


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Enter test email: ").strip()
    success = send_reports_email(
        to_address=email,
        patient_name="Test Patient",
        analysis_summary="This is a test email from the Health Impact Analyzer system.",
        overall_risk="Low",
        attachments=[],
    )
    print("SUCCESS: Sent!" if success else "FAILED: check SMTP config in .env")
