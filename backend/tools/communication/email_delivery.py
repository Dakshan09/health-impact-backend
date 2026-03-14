"""
Email Delivery — SMTP with HTTP Relay Fallback
Sends health reports via SMTP directly, or via Supabase Edge Function if SMTP is blocked.

Configuration (in .env):
    SMTP_HOST     = smtp.gmail.com
    SMTP_PORT     = 587
    SMTP_EMAIL    = your_email@gmail.com
    SMTP_PASSWORD = your_app_password
    SUPABASE_URL  = https://xxx.supabase.co
    SUPABASE_SERVICE_ROLE_KEY = sb_secret_xxx
"""

import os
import json
import smtplib
import base64
import traceback
import mimetypes
import urllib.request
import urllib.error
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
    attachments: list[str],
) -> bool:
    """
    Send health reports email with file attachments.
    Tries direct SMTP first, falls back to Supabase Edge Function HTTP relay.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_email or not smtp_password:
        print("SMTP credentials not configured (SMTP_EMAIL / SMTP_PASSWORD missing)")
        return False

    subject = f"Your Health Impact Analysis Report -- {patient_name}"
    risk_color = {"High": "#ef4444", "Moderate": "#f59e0b", "Low": "#22c55e"}.get(overall_risk, "#6b7280")
    html_body = _build_email_html(patient_name, analysis_summary, overall_risk, risk_color)
    plain_body = _build_email_plain(patient_name, overall_risk)

    # --- Method 1: Try direct SMTP (STARTTLS then SSL) ---
    smtp_sent = _try_smtp_send(
        smtp_host, smtp_port, smtp_email, smtp_password,
        to_address, subject, html_body, plain_body, attachments,
    )
    if smtp_sent:
        return True

    # --- Method 2: Fall back to Supabase Edge Function HTTP relay ---
    print("INFO: Direct SMTP failed. Trying Supabase Edge Function relay...")
    edge_sent = _try_edge_function_send(
        smtp_host, smtp_email, smtp_password,
        to_address, subject, html_body, plain_body, attachments,
    )
    if edge_sent:
        return True

    print("FAILED: All email methods failed.")
    return False


def _try_smtp_send(
    smtp_host, smtp_port, smtp_email, smtp_password,
    to_address, subject, html_body, plain_body, attachments,
) -> bool:
    """Try sending via direct SMTP (STARTTLS on 587, then SSL on 465)."""
    msg = _build_mime_message(smtp_email, to_address, subject, html_body, plain_body, attachments)

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
            print(f"SUCCESS: Email sent to {to_address} via SMTP {method}")
            return True
        except OSError as e:
            print(f"WARN: SMTP {method} failed (OSError): {e}")
            continue
        except smtplib.SMTPAuthenticationError:
            print("FAILED: SMTP Authentication failed.")
            return False
        except Exception as e:
            print(f"WARN: SMTP {method} failed: {e}")
            continue
    return False


def _try_edge_function_send(
    smtp_host, smtp_email, smtp_password,
    to_address, subject, html_body, plain_body, attachments,
) -> bool:
    """Send email via Supabase Edge Function (HTTP relay)."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    if not supabase_url or not service_role_key:
        print("WARN: Supabase URL or service role key not configured for Edge Function relay.")
        return False

    edge_url = f"{supabase_url}/functions/v1/send-email"

    # Build attachment list (base64-encoded)
    att_list = []
    for file_path in (attachments or []):
        if not file_path or not os.path.exists(file_path):
            continue
        with open(file_path, "rb") as f:
            file_data = f.read()
        mime_type, _ = mimetypes.guess_type(file_path)
        att_list.append({
            "filename": os.path.basename(file_path),
            "content": base64.b64encode(file_data).decode("ascii"),
            "content_type": mime_type or "application/octet-stream",
        })

    payload = {
        "to": to_address,
        "subject": subject,
        "html": html_body,
        "text": plain_body,
        "from_name": "Health Impact Analyzer",
        "smtp_email": smtp_email,
        "smtp_password": smtp_password,
        "smtp_host": smtp_host,
        "smtp_port": 465,
        "attachments": att_list,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        edge_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {service_role_key}",
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("email_sent"):
            print(f"SUCCESS: Email sent to {to_address} via Supabase Edge Function")
            return True
        else:
            print(f"WARN: Edge Function returned: {result}")
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"WARN: Edge Function HTTP error {e.code}: {body[:300]}")
        return False
    except Exception as e:
        print(f"WARN: Edge Function request failed: {e}")
        return False


def _build_mime_message(from_email, to_email, subject, html_body, plain_body, attachments):
    """Build a MIME message with HTML body and file attachments."""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"Health Impact Analyzer <{from_email}>"
    msg["To"] = to_email

    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(plain_body, "plain"))
    body_part.attach(MIMEText(html_body, "html"))
    msg.attach(body_part)

    for file_path in (attachments or []):
        if not file_path or not os.path.exists(file_path):
            continue
        _attach_file(msg, file_path)

    return msg


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
    summary_preview = ""
    if analysis_summary:
        lines = [l.strip() for l in analysis_summary.split("\\n") if l.strip() and not l.strip().startswith("#")]
        summary_preview = " ".join(lines[:4])[:500]
        if len(summary_preview) == 500:
            summary_preview += "..."

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0fdf4;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08);">
  <tr><td style="background:linear-gradient(135deg,#1a6b3c 0%,#2e8b57 100%);padding:32px 36px;">
    <h1 style="color:white;margin:0;font-size:22px;">Health Impact Analysis Report</h1>
    <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:14px;">
      Prepared for <strong>{patient_name}</strong> &middot; {datetime.now().strftime("%B %d, %Y")}
    </p>
  </td></tr>
  <tr><td style="padding:24px 36px 0;">
    <div style="display:inline-block;background:{risk_color}15;border:2px solid {risk_color};
                border-radius:99px;padding:8px 24px;font-weight:700;color:{risk_color};font-size:15px;">
      Overall Risk: {overall_risk}
    </div>
  </td></tr>
  <tr><td style="padding:20px 36px;">
    <p style="margin:0 0 12px;color:#374151;font-size:15px;">Dear <strong>{patient_name}</strong>,</p>
    <p style="margin:0 0 12px;color:#6b7280;font-size:14px;line-height:1.7;">
      Your personalized health impact analysis is complete. Please find your reports attached.
    </p>
    {f'<p style="margin:0;color:#374151;font-size:14px;background:#f8fafc;border-left:3px solid #2e8b57;padding:12px 16px;border-radius:0 8px 8px 0;"><em>{summary_preview}</em></p>' if summary_preview else ''}
  </td></tr>
  <tr><td style="padding:0 36px 20px;">
    <h2 style="color:#1a6b3c;font-size:16px;margin:0 0 12px;">Your Attached Reports</h2>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:10px 14px;background:#f0fdf4;border-radius:8px;border:1px solid #d1fae5;">
        <strong style="color:#1a6b3c;font-size:14px;">Clinical Report (PDF)</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Full medical analysis with AI recommendations</p>
      </td></tr>
      <tr><td style="padding:6px 0;"></td></tr>
      <tr><td style="padding:10px 14px;background:#faf5ff;border-radius:8px;border:1px solid #e9d5ff;">
        <strong style="color:#7c3aed;font-size:14px;">Visualization Report</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Color-coded risk charts and lifestyle scores</p>
      </td></tr>
      <tr><td style="padding:6px 0;"></td></tr>
      <tr><td style="padding:10px 14px;background:#f0fdf4;border-radius:8px;border:1px solid #d1fae5;">
        <strong style="color:#059669;font-size:14px;">90-Day Intervention Schedule (Excel)</strong>
        <p style="margin:4px 0 0;color:#6b7280;font-size:12px;">Personalized daily habits and weekly goals</p>
      </td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:16px 36px;background:#fef9c3;border-top:1px solid #fde047;">
    <p style="margin:0;color:#854d0e;font-size:12px;line-height:1.6;">
      <strong>Medical Disclaimer:</strong> These reports are for informational purposes only.
      Always consult a qualified healthcare professional for diagnosis and treatment.
    </p>
  </td></tr>
  <tr><td style="padding:20px 36px;text-align:center;">
    <p style="margin:0;color:#9ca3af;font-size:11px;">
      Generated by <strong>Health Impact Analyzer</strong> &middot; {datetime.now().strftime("%Y-%m-%d %H:%M")}
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
