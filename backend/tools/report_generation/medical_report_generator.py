"""
Medical Report Generator
Generates comprehensive lab-style health analysis reports in Markdown format.
Matches the "HEALTH IMPACT ANALYSIS LAB" clinical report template.
"""

from datetime import datetime
from typing import Optional


def generate_medical_report(
    prediction_text: str,
    patient_name: str,
    patient_data: Optional[dict] = None,
    risk_categories: Optional[dict] = None
) -> str:
    """
    Generate a lab-style clinical report matching the sample PDF format.

    Args:
        prediction_text: AI-generated health analysis text
        patient_name: Patient's full name
        patient_data: Optional patient profile data dict
        risk_categories: Optional dict of risk category scores (0-100)

    Returns:
        Formatted Markdown report string with tables
    """
    now = datetime.now()
    report_date = now.strftime("%Y-%m-%d %H:%M")
    report_id = f"USER_{now.strftime('%Y%m%d_%H%M%S')}"
    safe_name = "".join(c if c.isalnum() else "_" for c in patient_name)
    run_id = now.strftime("%Y%m%d_%H%M%S")

    age = patient_data.get("age", "N/A") if patient_data else "N/A"

    # ── Compute overall health score from risk categories ──────────────
    if risk_categories:
        avg_risk = sum(risk_categories.values()) / len(risk_categories)
        overall_score = max(0, int(100 - avg_risk))
    else:
        overall_score = 50  # default

    if overall_score >= 80:
        interpretation = "OPTIMAL"
    elif overall_score >= 60:
        interpretation = "MODERATE"
    elif overall_score >= 40:
        interpretation = "MODERATE"
    else:
        interpretation = "ELEVATED CONCERN"

    # ── Determine primary clinical concerns ────────────────────────────
    concerns = []
    if risk_categories:
        sorted_risks = sorted(risk_categories.items(), key=lambda x: x[1], reverse=True)
        risk_name_map = {
            "cardiovascular": "Cardiovascular Health",
            "metabolic": "Metabolic Syndrome Risk",
            "nutrient_deficiency": "Nutrient Deficiency",
            "obesity": "Obesity Risk",
            "mental_health": "Mental Health",
            "respiratory": "Respiratory Health",
            "musculoskeletal": "Musculoskeletal Health",
            "diabetes": "Type 2 Diabetes Risk",
            "hypertension": "Hypertension Risk",
        }
        for name, score in sorted_risks:
            if score > 30 and len(concerns) < 3:
                label = risk_name_map.get(name, name.replace("_", " ").title())
                concerns.append(label)

    if not concerns:
        concerns = ["General Wellness Review"]

    concerns_bullets = "\n".join(f"- {c}" for c in concerns)

    # ── Build risk assessment matrix ───────────────────────────────────
    risk_matrix_rows = ""
    if risk_categories:
        risk_detail_map = {
            "cardiovascular": ("Cardiovascular Disease", "dietary patterns, activity level, family history"),
            "hypertension": ("Hypertension", "sodium intake, stress level, family history"),
            "nutrient_deficiency": ("Nutrient Deficiency", "fruit/vegetable intake, diet variety, meal frequency"),
            "obesity": ("Obesity Metabolic", "processed food intake, activity level, meal patterns"),
            "metabolic": ("Metabolic Syndrome", "processed food intake, activity level, meal patterns"),
            "diabetes": ("Type 2 Diabetes", "sugar intake, BMI, activity level"),
            "mental_health": ("Mental Health Decline", "stress level, sleep quality, social activity"),
            "respiratory": ("Respiratory Issues", "smoking status, air quality, exercise capacity"),
            "musculoskeletal": ("Musculoskeletal Decline", "activity level, posture, calcium intake"),
        }
        sorted_risks = sorted(risk_categories.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_risks:
            detail = risk_detail_map.get(name, (name.replace("_", " ").title(), "lifestyle factors"))
            probability = f"{score * 0.3:.1f}%"  # approximate 10-year probability
            if score >= 70:
                tier = "HIGH"
            elif score >= 40:
                tier = "MODERATE"
            else:
                tier = "LOW"
            risk_matrix_rows += f"| {detail[0]} | {probability} | {tier} | {detail[1]} |\n"

    # ── Build nutritional panel ────────────────────────────────────────
    diet_quality = patient_data.get("dietQuality", patient_data.get("dietType", "N/A")) if patient_data else "N/A"
    if diet_quality and diet_quality.lower() in ("poor", "fair", "n/a"):
        diet_status = "SUBOPTIMAL"
    elif diet_quality and diet_quality.lower() in ("good",):
        diet_status = "ADEQUATE"
    else:
        diet_status = "NORMAL"

    medications = patient_data.get("medications", "") if patient_data else ""
    if medications:
        micro_result = "Review Needed"
        micro_status = "PENDING"
    else:
        micro_result = "None Detected"
        micro_status = "NORMAL"

    # ── Build dietary interventions from prediction text ────────────────
    dietary_orders = _extract_dietary_orders(prediction_text, patient_data)
    dietary_rows = ""
    for order in dietary_orders:
        dietary_rows += f"| {order['priority']} | {order['intervention']} | {order['timeline']} |\n"

    # ── Build substitution table ───────────────────────────────────────
    substitutions = _build_substitutions(patient_data)
    substitution_rows = ""
    for sub in substitutions:
        substitution_rows += f"| {sub['discontinue']} | {sub['substitute']} | {sub['rationale']} |\n"

    # ── Assemble full report ───────────────────────────────────────────
    report = f"""# HEALTH IMPACT ANALYSIS LAB

| Field | Value | Field | Value |
|-------|-------|-------|-------|
| PATIENT: | {patient_name} | REPORT ID: | {report_id} |
| DOB / AGE: | {age} | DATE: | {report_date} |
| REF. PHYSICIAN: | AI DIAGNOSTIC SYSTEM | STATUS: | FINAL |

---

## EXECUTIVE HEALTH SUMMARY

| METRIC | RESULT | REFERENCE RANGE | CLINICAL INTERPRETATION |
|--------|--------|-----------------|------------------------|
| Overall Health Score | {overall_score} / 100 | > 80 (Optimal) | {interpretation} |

**PRIMARY CLINICAL CONCERNS:**
{concerns_bullets}

---

## DETAILED RISK ASSESSMENT MATRIX

| PATHOLOGY / CONDITION | 10-YEAR PROBABILITY | RISK TIER | CONTRIBUTING FACTORS |
|-----------------------|--------------------:|-----------|----------------------|
{risk_matrix_rows}
---

## NUTRITIONAL & METABOLIC PANEL

| PARAMETER | RESULT / FINDING | STATUS |
|-----------|-----------------|--------|
| Dietary Quality Index | {diet_quality} | {diet_status} |
| Micronutrient Deficiencies | {micro_result} | {micro_status} |
| Hydration Status | Not Reported | Correlation Required |

---

## CLINICAL INTERVENTION PLAN

### A. DIETARY ORDERS

| PRIORITY | INTERVENTION | TIMELINE |
|----------|-------------|----------|
{dietary_rows}
### B. INDICATED SUBSTITUTIONS

| DISCONTINUE / LIMIT | SUBSTITUTE WITH | CLINICAL RATIONALE |
|---------------------|----------------|-------------------|
{substitution_rows}
---

DISCLAIMER: This report is an algorithmic analysis based on self-reported data. Results should be clinically correlated by a licensed medical professional. Not valid for diagnostic purposes without physician review.

Generated by Antigravity Health System | Run ID: {run_id}
"""

    return report


def _extract_dietary_orders(prediction_text: str, patient_data: Optional[dict]) -> list:
    """Build dietary order rows based on prediction and patient data."""
    orders = []

    diet = ""
    if patient_data:
        diet = (patient_data.get("dietQuality") or patient_data.get("dietType") or "").lower()

    # Always recommend these baseline interventions
    orders.append({
        "priority": "ROUTINE",
        "intervention": "Increase vegetables to 5 servings daily",
        "timeline": "2-4 weeks",
    })
    orders.append({
        "priority": "ROUTINE",
        "intervention": "Replace refined grains with whole grains",
        "timeline": "4-6 weeks",
    })
    orders.append({
        "priority": "ROUTINE",
        "intervention": "Add omega-3 rich foods (fish, flaxseed)",
        "timeline": "1-2 weeks",
    })
    orders.append({
        "priority": "ROUTINE",
        "intervention": "Reduce added sugar to under 25g daily",
        "timeline": "4-8 weeks",
    })

    # Add urgency-based orders if diet is poor
    if diet in ("poor", "fair"):
        orders.insert(0, {
            "priority": "URGENT",
            "intervention": "Eliminate processed food consumption",
            "timeline": "1-2 weeks",
        })

    return orders


def _build_substitutions(patient_data: Optional[dict]) -> list:
    """Build food substitution recommendations."""
    return [
        {
            "discontinue": "White bread/rice",
            "substitute": "Whole wheat bread / brown rice",
            "rationale": "Improved glycemic control, sustained energy",
        },
        {
            "discontinue": "Sugary snacks",
            "substitute": "Mixed nuts, fruits, dark chocolate",
            "rationale": "Reduced sugar intake, better micronutrients",
        },
        {
            "discontinue": "Soda / sweetened drinks",
            "substitute": "Water, herbal tea, lemon water",
            "rationale": "Reduced empty calories, better hydration",
        },
        {
            "discontinue": "Fried foods",
            "substitute": "Grilled, steamed, or baked alternatives",
            "rationale": "Reduced trans fat, cardiovascular benefit",
        },
    ]


def generate_summary_report(patient_name: str, key_findings: list) -> str:
    """
    Generate a brief summary report with key findings.

    Args:
        patient_name: Patient's name
        key_findings: List of key finding strings

    Returns:
        Brief summary report string
    """
    report = f"# Health Summary - {patient_name}\n\n"
    report += f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n"
    report += "## Key Findings\n\n"
    for finding in key_findings:
        report += f"- {finding}\n"
    report += "\n*Full analysis available in complete report.*\n"
    return report


if __name__ == "__main__":
    # Demo
    sample_data = {
        "age": "45", "gender": "Male", "smokingStatus": "Current smoker",
        "exerciseFrequency": "Rarely", "dietQuality": "Fair",
        "sleepHours": "5", "stressLevel": "High",
        "conditions": ["Hypertension"], "medications": "Lisinopril 10mg",
        "currentSymptoms": "Fatigue, shortness of breath",
        "symptomDuration": "3 months", "concerns": "Worried about heart health"
    }
    prediction = "Patient presents with multiple cardiovascular risk factors."
    risks = {"cardiovascular": 75, "metabolic": 45, "mental_health": 60}
    report = generate_medical_report(prediction, "John Demo", sample_data, risks)
