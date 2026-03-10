"""
Health Dashboard Creator
Generates visual health risk charts and dashboard data.
"""

import json
import os
from datetime import datetime


def create_risk_visualization(prediction_text: str, patient_data: dict) -> dict:
    """
    Create a structured dashboard visualization from prediction text and patient data.
    Returns a dict with chart data suitable for rendering.
    """
    # Parse risk levels from prediction text keywords
    risk_scores = _extract_risk_scores(prediction_text, patient_data)

    dashboard = {
        "patient_name": patient_data.get("fullName", "Anonymous"),
        "generated_at": datetime.now().isoformat(),
        "overall_risk": _compute_overall_risk(risk_scores),
        "risk_categories": risk_scores,
        "lifestyle_scores": _compute_lifestyle_scores(patient_data),
        "recommendations_count": prediction_text.lower().count("recommend"),
    }

    return dashboard


def _extract_risk_scores(prediction_text: str, patient_data: dict) -> dict:
    """Extract category-level risk scores based on keywords and patient data."""
    text_lower = prediction_text.lower()

    scores = {
        "cardiovascular": 0,
        "metabolic": 0,
        "mental_health": 0,
        "respiratory": 0,
        "musculoskeletal": 0,
    }

    # Keyword-based risk detection from prediction text
    keyword_map = {
        "cardiovascular": ["heart", "cardiac", "blood pressure", "hypertension", "cholesterol", "stroke"],
        "metabolic": ["diabetes", "glucose", "insulin", "obesity", "metabolic", "weight"],
        "mental_health": ["stress", "anxiety", "depression", "mental", "sleep", "fatigue"],
        "respiratory": ["lung", "respiratory", "asthma", "breathing", "copd", "smoking"],
        "musculoskeletal": ["joint", "muscle", "bone", "arthritis", "back pain", "mobility"],
    }

    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text_lower:
                scores[category] += 20  # Each keyword match adds 20 points

    # Cap at 100
    for key in scores:
        scores[key] = min(scores[key], 100)

    # Boost based on direct patient lifestyle data
    smoking = patient_data.get("smokingStatus", "").lower()
    if "current" in smoking or "heavy" in smoking:
        scores["respiratory"] = min(scores["respiratory"] + 30, 100)
        scores["cardiovascular"] = min(scores["cardiovascular"] + 20, 100)

    exercise = patient_data.get("exerciseFrequency", "").lower()
    if "never" in exercise or "rarely" in exercise:
        scores["cardiovascular"] = min(scores["cardiovascular"] + 20, 100)
        scores["metabolic"] = min(scores["metabolic"] + 20, 100)

    stress = patient_data.get("stressLevel", "").lower()
    if "high" in stress or "very high" in stress:
        scores["mental_health"] = min(scores["mental_health"] + 30, 100)

    return scores


def _compute_overall_risk(risk_scores: dict) -> str:
    """Compute overall risk level label from category scores."""
    avg = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0
    if avg >= 70:
        return "High"
    elif avg >= 40:
        return "Moderate"
    else:
        return "Low"


def _compute_lifestyle_scores(patient_data: dict) -> dict:
    """Compute lifestyle quality scores (0-100, higher = better)."""
    scores = {}

    # Diet quality
    diet = patient_data.get("dietQuality", "").lower()
    diet_map = {"excellent": 95, "good": 75, "fair": 50, "poor": 25}
    scores["diet"] = next((v for k, v in diet_map.items() if k in diet), 50)

    # Sleep (assuming 7-9 hours is optimal)
    try:
        sleep_hours = float(patient_data.get("sleepHours", 7))
        if 7 <= sleep_hours <= 9:
            scores["sleep"] = 90
        elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
            scores["sleep"] = 65
        else:
            scores["sleep"] = 35
    except (ValueError, TypeError):
        scores["sleep"] = 50

    # Exercise
    exercise = patient_data.get("exerciseFrequency", "").lower()
    exercise_map = {"daily": 95, "5": 85, "3": 70, "weekly": 60, "rarely": 30, "never": 10}
    scores["exercise"] = next((v for k, v in exercise_map.items() if k in exercise), 50)

    # Stress (inverse scoring)
    stress = patient_data.get("stressLevel", "").lower()
    stress_map = {"low": 90, "moderate": 60, "high": 35, "very high": 15}
    scores["stress_management"] = next((v for k, v in stress_map.items() if k in stress), 50)

    # Smoking
    smoking = patient_data.get("smokingStatus", "").lower()
    if "never" in smoking or "non" in smoking:
        scores["smoking"] = 100
    elif "former" in smoking or "quit" in smoking:
        scores["smoking"] = 70
    elif "occasional" in smoking:
        scores["smoking"] = 40
    else:
        scores["smoking"] = 10

    return scores


def save_dashboard_json(dashboard: dict, output_path: str) -> str:
    """Save dashboard data as JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2)
    print(f"Dashboard data saved to: {output_path}")
    return output_path


def print_dashboard_summary(dashboard: dict):
    """Print a human-readable summary of the dashboard."""
    print("\n" + "=" * 60)
    print(f"  HEALTH DASHBOARD: {dashboard['patient_name']}")
    print(f"  Generated: {dashboard['generated_at'][:10]}")
    print("=" * 60)
    print(f"\n  Overall Risk Level: {dashboard['overall_risk']}")

    print("\n  Risk Categories:")
    for cat, score in dashboard["risk_categories"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        label = cat.replace("_", " ").title()
        print(f"    {label:<20} [{bar}] {score}%")

    print("\n  Lifestyle Scores:")
    for cat, score in dashboard["lifestyle_scores"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        label = cat.replace("_", " ").title()
        print(f"    {label:<20} [{bar}] {score}%")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Demo mode
    sample_data = {
        "fullName": "Demo Patient",
        "age": "45",
        "gender": "Male",
        "smokingStatus": "Current smoker",
        "exerciseFrequency": "Rarely",
        "dietQuality": "Fair",
        "sleepHours": "5",
        "stressLevel": "High",
    }
    sample_prediction = "High risk of cardiovascular disease. Metabolic risk due to poor diet. Mental health concerns from stress and sleep deprivation. Respiratory risk from smoking."
    dashboard = create_risk_visualization(sample_prediction, sample_data)
    print_dashboard_summary(dashboard)
