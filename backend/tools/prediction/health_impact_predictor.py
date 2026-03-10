import os
import litellm
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    fullName: str = ""
    age: str = ""
    gender: str = ""
    email: str = ""
    phone: str = ""
    conditions: list[str] = []
    medications: str = ""
    allergies: str = ""
    surgeries: str = ""
    familyHistory: str = ""
    smokingStatus: str = ""
    alcoholConsumption: str = ""
    exerciseFrequency: str = ""
    dietQuality: str = ""
    sleepHours: str = ""
    stressLevel: str = ""
    currentSymptoms: str = ""
    symptomDuration: str = ""
    concerns: str = ""

def generate_health_prediction(data: dict) -> str:
    prompt = f"""
You are an expert AI Health Analyzer. Based on the following user data, provide a comprehensive health analysis, potential risk factors, and personalized recommendations. Format your response strictly in Markdown.

Patient Profile:
- Age: {data.get("age")}
- Gender: {data.get("gender")}
- Conditions: {", ".join(data.get("conditions", []))}
- Medications: {data.get("medications")}
- Allergies: {data.get("allergies")}
- Surgeries: {data.get("surgeries")}
- Family History: {data.get("familyHistory")}

Lifestyle:
- Smoking: {data.get("smokingStatus")}
- Alcohol: {data.get("alcoholConsumption")}
- Exercise: {data.get("exerciseFrequency")}
- Diet: {data.get("dietQuality")}
- Sleep: {data.get("sleepHours")} hours
- Stress: {data.get("stressLevel")}

Current Concerns:
- Symptoms: {data.get("currentSymptoms")} ({data.get("symptomDuration")})
- Concerns: {data.get("concerns")}

Please provide:
1. Executive Summary
2. Key Risk Factors
3. Lifestyle Recommendations
4. Recommended Screenings or Actions
"""

    # Check for keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if not gemini_key and not groq_key:
        return "⚠️ **API Keys Not Configured**\n\nPlease configure `GROQ_API_KEY` or `GEMINI_API_KEY` in the `.env` file to enable AI predictions.\n\n*Mock Analysis:* Based on the provided data, we recommend consulting a healthcare professional for a tailored assessment."

    model = "gemini/gemini-pro" if gemini_key else "groq/llama3-8b-8192"

    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating prediction from AI model: {str(e)}"
