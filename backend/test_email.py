from tools.communication.email_delivery import send_reports_email
import os

with open("dummy1.pdf", "w") as f: f.write("dummy pdf")
with open("dummy2.html", "w") as f: f.write("<html>dummy html</html>")

success = send_reports_email(
    to_address="test@example.com",
    patient_name="Tester",
    analysis_summary="This is a test summary",
    overall_risk="Low",
    attachments=["dummy1.pdf", "dummy2.html"]
)
print("SUCCESS:", success)
