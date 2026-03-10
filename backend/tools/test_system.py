"""
System Test Script
Tests all components of the Health Impact Analyzer system.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all system tests."""
    print("=" * 60)
    print("  Health Impact Analyzer - System Test")
    print("=" * 60)
    print()

    results = {}

    # Test 1: Environment
    results["Environment"] = test_environment()

    # Test 2: Prediction model
    results["Health Predictor"] = test_predictor()

    # Test 3: Medical report generator
    results["Report Generator"] = test_report_generator()

    # Test 4: PDF compiler
    results["PDF Compiler"] = test_pdf_compiler()

    # Test 5: Dashboard creator
    results["Dashboard Creator"] = test_dashboard_creator()

    # Test 6: Schedule generator
    results["Schedule Generator"] = test_schedule_generator()

    # Test 7: Email delivery
    results["Email Delivery"] = test_email_delivery()

    # Test 8: Data logging
    results["Data Logger"] = test_data_logger()

    # Summary
    print()
    print("=" * 60)
    print("  TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0
    warned = 0

    for test_name, (status, message) in results.items():
        icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}.get(status, "[?]")
        print(f"  {icon} {test_name:<25} {message}")
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        else:
            warned += 1

    print()
    print(f"  Results: {passed} passed, {warned} warnings, {failed} failed")
    print()

    if failed == 0:
        print("  [OK] System is ready! Run: python main.py")
    else:
        print("  [!!] Fix the failed tests before running the system.")
    print("=" * 60)

    return failed == 0


def test_environment():
    """Test environment configuration."""
    print("[1/8] Testing environment...")
    from dotenv import load_dotenv
    load_dotenv()

    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if groq_key and groq_key != "your_groq_api_key_here":
        return "PASS", "GROQ_API_KEY configured"
    elif gemini_key and gemini_key != "your_gemini_api_key_here":
        return "PASS", "GEMINI_API_KEY configured"
    else:
        return "WARN", "No AI API key set (add to .env)"


def test_predictor():
    """Test health predictor module."""
    print("[2/8] Testing health predictor...")
    try:
        from tools.prediction.health_impact_predictor import generate_health_prediction, PredictionRequest

        sample = PredictionRequest(
            fullName="Test Patient",
            age="35",
            gender="Female",
            smokingStatus="Never",
            exerciseFrequency="3x per week",
            dietQuality="Good",
        )
        result = generate_health_prediction(sample.model_dump())

        if result and len(result) > 10:
            if "API Keys Not Configured" in result:
                return "WARN", "Module OK, but API key needed for AI predictions"
            return "PASS", "Health predictor working"
        return "FAIL", "Predictor returned empty result"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_report_generator():
    """Test medical report generator."""
    print("[3/8] Testing report generator...")
    try:
        from tools.report_generation.medical_report_generator import generate_medical_report

        report = generate_medical_report(
            "Test analysis text.", "Test Patient",
            {"age": "35", "gender": "Female"},
            {"cardiovascular": 30, "metabolic": 20}
        )

        if "Test Patient" in report and "Health Impact Analysis" in report:
            return "PASS", "Report generator working"
        return "FAIL", "Report missing expected content"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_pdf_compiler():
    """Test PDF compiler."""
    print("[4/8] Testing PDF compiler...")
    try:
        from tools.report_generation.pdf_compiler import compile_pdf, generate_output_path

        output = generate_output_path("TestPatient", ".tmp/user_reports")
        result = compile_pdf("# Test Report\n\nTest content.", output)

        if result and os.path.exists(result):
            os.remove(result)  # Clean up
            if result.endswith(".pdf"):
                return "PASS", "PDF compilation working (reportlab)"
            else:
                return "WARN", "PDF saved as HTML (install reportlab for PDF)"
        return "FAIL", "Output file not created"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_dashboard_creator():
    """Test dashboard creator."""
    print("[5/8] Testing dashboard creator...")
    try:
        from tools.visualization.health_dashboard_creator import create_risk_visualization

        dashboard = create_risk_visualization(
            "High cardiovascular risk. Metabolic concerns noted.",
            {"fullName": "Test Patient", "smokingStatus": "Never", "stressLevel": "Moderate"}
        )

        if "risk_categories" in dashboard and "overall_risk" in dashboard:
            return "PASS", f"Dashboard creator working (risk: {dashboard['overall_risk']})"
        return "FAIL", "Dashboard missing expected fields"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_schedule_generator():
    """Test schedule generator."""
    print("[6/8] Testing schedule generator...")
    try:
        from tools.intervention.schedule_generator import generate_intervention_schedule

        schedule = generate_intervention_schedule(
            {"fullName": "Test Patient"},
            {"cardiovascular": 60, "metabolic": 40},
            duration_days=30
        )

        if "phases" in schedule and "milestones" in schedule:
            return "PASS", f"Schedule generator working ({len(schedule['phases'])} phases)"
        return "FAIL", "Schedule missing expected fields"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_email_delivery():
    """Test email delivery module (dry run)."""
    print("[7/8] Testing email delivery...")
    try:
        from tools.communication.email_delivery import send_reports_email

        # Validate the function is importable and inspect its signature
        import inspect
        sig = inspect.signature(send_reports_email)
        params = list(sig.parameters)

        if "to_address" in params and "attachments" in params:
            smtp_email = os.getenv("SMTP_EMAIL", "")
            if smtp_email and "@" in smtp_email:
                return "PASS", f"SMTP email configured ({smtp_email})"
            else:
                return "WARN", "Module OK — set SMTP_EMAIL + SMTP_PASSWORD in .env to enable email"
        return "FAIL", "send_reports_email missing expected parameters"
    except Exception as e:
        return "FAIL", f"Error: {e}"


def test_data_logger():
    """Test data logger (local fallback)."""
    print("[8/8] Testing data logger...")
    try:
        from tools.data_management.google_sheets_logger import log_data

        # Will use local fallback since no sheet ID
        log_data({"fullName": "Test Patient", "age": "35"})

        log_dir = os.path.join(".tmp", "cleaned_data")
        if os.path.exists(log_dir):
            files = os.listdir(log_dir)
            test_files = [f for f in files if "Test_Patient" in f]
            for tf in test_files:
                os.remove(os.path.join(log_dir, tf))

        return "WARN", "Local logging OK, add GOOGLE_SHEET_ID for sheets sync"
    except Exception as e:
        return "FAIL", f"Error: {e}"


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
