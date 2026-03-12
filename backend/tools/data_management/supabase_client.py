"""
Supabase Client
Handles all database operations for the Health Impact Analyzer.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Force load from the backend root .env (works both locally and on Render)
_backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(_backend_env)

_client = None


def _get_client():
    """Initialize and return the Supabase client (lazy singleton)."""
    global _client
    if _client is not None:
        return _client

    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError(
            "supabase-py not installed. Run: pip install supabase"
        )

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env"
        )

    _client = create_client(url, key)
    return _client


def save_assessment(patient_data: dict, ai_analysis: str = "", overall_risk: str = "") -> str:
    """
    Save a patient health assessment to Supabase.

    Args:
        patient_data: Raw form data dict from the frontend (camelCase keys)
        ai_analysis: The AI-generated analysis text
        overall_risk: Overall risk level string (High/Moderate/Low)

    Returns:
        UUID of the inserted row, or empty string on failure
    """
    try:
        client = _get_client()

        # Map camelCase frontend keys to snake_case DB columns
        row = {
            "full_name": patient_data.get("fullName", ""),
            "email": patient_data.get("email", ""),
            "age": str(patient_data.get("age", "")),
            "gender": patient_data.get("gender", ""),
            "height": patient_data.get("height", ""),
            "weight": patient_data.get("weight", ""),
            "ethnicity": patient_data.get("ethnicity", ""),
            "location": patient_data.get("location", ""),
            "existing_conditions": patient_data.get("existingConditions") or patient_data.get("conditions", []),
            "current_medications": patient_data.get("currentMedications") or patient_data.get("medications", ""),
            "family_history": patient_data.get("familyHistory", []),
            "blood_pressure": patient_data.get("bloodPressure", ""),
            "fasting_glucose": patient_data.get("fastingGlucose", ""),
            "cholesterol": patient_data.get("cholesterol", ""),
            "processed_food_consumption": patient_data.get("processedFoodConsumption", ""),
            "sugar_consumption": patient_data.get("sugarConsumption", ""),
            "water_intake": str(patient_data.get("waterIntake", "")),
            "diet_type": patient_data.get("dietType", ""),
            "meal_frequency": str(patient_data.get("mealFrequency", "")),
            "fruit_veg_servings": str(patient_data.get("fruitVegServings", "")),
            "exercise_frequency": patient_data.get("exerciseFrequency", ""),
            "exercise_type": patient_data.get("exerciseType", ""),
            "sleep_hours": str(patient_data.get("sleepHours", "")),
            "sleep_quality": patient_data.get("sleepQuality", ""),
            "smoking_status": patient_data.get("smokingStatus", ""),
            "alcohol_consumption": patient_data.get("alcoholConsumption", ""),
            "stress_level": patient_data.get("stressLevel", ""),
            "screen_time": str(patient_data.get("screenTime", "")),
            "ai_analysis": ai_analysis,
            "overall_risk": overall_risk,
        }

        result = client.table("health_assessments").insert(row).execute()

        if result.data and len(result.data) > 0:
            assessment_id = result.data[0].get("id", "")
            print(f"OK: Assessment saved to Supabase (ID: {assessment_id})")
            return assessment_id
        return ""

    except Exception as e:
        print(f"WARN: Supabase save_assessment failed: {e}".encode("ascii", "replace").decode("ascii"))
        return ""


def save_report_record(
    assessment_id: str,
    patient_name: str,
    patient_email: str,
    clinical_path: str = "",
    schedule_path: str = "",
    visualization_path: str = "",
    email_sent: bool = False,
) -> str:
    """
    Save a report generation record to Supabase.

    Returns:
        UUID of the inserted record, or empty string on failure
    """
    try:
        client = _get_client()

        row = {
            "assessment_id": assessment_id if assessment_id else None,
            "patient_name": patient_name,
            "patient_email": patient_email,
            "clinical_report_path": clinical_path,
            "schedule_report_path": schedule_path,
            "visualization_report_path": visualization_path,
            "email_sent": email_sent,
            "email_sent_at": datetime.utcnow().isoformat() if email_sent else None,
        }

        result = client.table("generated_reports").insert(row).execute()

        if result.data and len(result.data) > 0:
            report_id = result.data[0].get("id", "")
            print(f"OK: Report record saved to Supabase (ID: {report_id})")
            return report_id
        return ""

    except Exception as e:
        print(f"WARN: Supabase save_report_record failed: {e}".encode("ascii", "replace").decode("ascii"))
        return ""
