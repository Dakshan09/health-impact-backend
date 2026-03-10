"""
Intervention Schedule Generator
Creates personalized 30-day health intervention plans with 4-week structure.
Matches the sample Excel schedule format: Overview, Daily Schedule, Week 1-4.
"""

from datetime import datetime, timedelta
from typing import Optional
import random


# ─── Meal Data ────────────────────────────────────────────────────────────────

BREAKFASTS = [
    "Greek Yogurt Parfait (5 min)",
    "Overnight Oats (5 min (night before))",
    "Smoothie Bowl (10 min)",
    "Whole Grain Toast with Avocado (10 min)",
    "Veggie Omelet (15 min)",
]

LUNCHES = [
    "Mediterranean Salad (15 min)",
    "Tuna Salad Lettuce Cups (15 min)",
    "Grilled Chicken Wrap (20 min)",
    "Quinoa Buddha Bowl (25 min)",
    "Lentil Soup (30 min)",
]

DINNERS = [
    "Black Bean Tacos (20 min)",
    "Stir-Fry with Brown Rice (25 min)",
    "Grilled Fish with Quinoa Salad (30 min)",
    "Baked Salmon with Vegetables (35 min)",
    "Mediterranean Baked Chicken (40 min)",
]

DEFAULT_SNACKS = "Fruit or nuts, Vegetables with hummus"
DEFAULT_HYDRATION = "8 glasses (64 oz)"

# ─── Week Phase Definitions ──────────────────────────────────────────────────

WEEK_PHASES = {
    1: {
        "name": "Foundation Building",
        "goals": [
            "Establish baseline habits",
            "Begin food diary tracking",
            "Add one vegetable serving per day",
            "Drink 8 glasses of water daily",
        ],
    },
    2: {
        "name": "Building Momentum",
        "goals": [
            "Replace sweetened beverages with water",
            "Add second vegetable serving",
            "Establish regular meal times",
            "Start 10-minute daily walks",
        ],
    },
    3: {
        "name": "Habit Consolidation",
        "goals": [
            "Maintain previous changes",
            "Add one fruit serving",
            "Reduce processed food by 50%",
            "Increase walk to 20 minutes",
        ],
    },
    4: {
        "name": "Progress Assessment",
        "goals": [
            "Review all changes made",
            "Identify challenges and solutions",
            "Plan for month 2",
            "Celebrate achievements",
        ],
    },
}

# ─── Shopping List Data ──────────────────────────────────────────────────────

SHOPPING_LIST = {
    "Produce": [
        "Mixed salad greens", "Spinach", "Broccoli", "Carrots",
        "Tomatoes", "Onions", "Garlic", "Avocados",
    ],
    "Fruits": [
        "Apples", "Bananas", "Berries (fresh or frozen)", "Lemons", "Oranges",
    ],
    "Proteins": [
        "Chicken breast", "Salmon or fish", "Eggs", "Greek yogurt", "Tofu or legumes",
    ],
    "Grains": [
        "Oats", "Brown rice or quinoa", "Whole grain bread", "Whole wheat pasta",
    ],
    "Pantry": [
        "Olive oil", "Nuts (almonds, walnuts)", "Seeds (chia, flax)",
        "Herbs and spices", "Low-sodium broth",
    ],
}

# ─── Meal Prep Checklist ─────────────────────────────────────────────────────

MEAL_PREP = [
    "Wash and chop vegetables for the week",
    "Cook grains (rice, quinoa) in bulk",
    "Prepare overnight oats for 3 days",
    "Portion snacks into containers",
    "Marinate proteins for easy cooking",
]

# ─── Weekly Check-In Questions ───────────────────────────────────────────────

CHECK_IN_QUESTIONS = [
    "Which habits felt easiest to maintain?",
    "What were the biggest challenges?",
    "How is your energy level compared to last week?",
    "What would you do differently next week?",
]

# ─── Daily Focus Items ───────────────────────────────────────────────────────

WEEK1_DAILY_FOCUS = [
    "Track everything you eat today",
    "Clear pantry of processed snacks",
    "Plan meals for the week",
    "Practice mindful eating at one meal",
    "Try one new healthy recipe",
    "Prep meals for next week",
    "Review progress and adjust",
]

DEFAULT_DAILY_FOCUS = "Continue building healthy habits"


# ─── Core Principles ─────────────────────────────────────────────────────────

CORE_PRINCIPLES = [
    "Progress over perfection",
    "Small changes compound over time",
    "Listen to your body",
    "Celebrate every win",
]


def generate_intervention_schedule(
    patient_data: dict,
    risk_categories: dict,
    duration_days: int = 30,
    start_date: Optional[str] = None
) -> dict:
    """
    Generate a personalized 30-day intervention schedule.

    Args:
        patient_data: Patient profile dict
        risk_categories: Dict of risk category scores (0-100)
        duration_days: Plan duration (default 30 days)
        start_date: Start date string (ISO format), defaults to today

    Returns:
        Structured intervention schedule dict with:
        - overview info (dates, principles, milestones)
        - daily_schedule (30 days of meals + tracking)
        - weeks (4 weeks with goals, shopping, meal prep, check-in)
    """
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now()

    end = start + timedelta(days=duration_days)

    # Seed random based on patient name for reproducible meal plans
    patient_name = patient_data.get("fullName", "Anonymous")
    seed = sum(ord(c) for c in patient_name)
    rng = random.Random(seed)

    schedule = {
        "patient_name": patient_name,
        "plan_duration_days": duration_days,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),

        # Overview data
        "core_principles": CORE_PRINCIPLES,
        "milestones": _build_milestones(),

        # Daily Schedule (30 rows)
        "daily_schedule": _build_daily_schedule(rng, duration_days),

        # Week 1-4 detail sheets
        "weeks": _build_weeks(),
    }

    return schedule


def _build_milestones() -> list:
    """Build milestone checkpoints at Day 7, 14, 30."""
    return [
        {
            "day": 7,
            "checkpoint": "Day 7 Checkpoint",
            "actions": "Reflect on progress, Measure and record metrics, Adjust plan",
        },
        {
            "day": 14,
            "checkpoint": "Day 14 Checkpoint",
            "actions": "Reflect on progress, Measure and record metrics, Adjust plan",
        },
        {
            "day": 30,
            "checkpoint": "Day 30 Checkpoint",
            "actions": "Reflect on progress, Measure and record metrics, Adjust plan",
        },
    ]


def _build_daily_schedule(rng: random.Random, duration_days: int) -> list:
    """Build 30-day daily schedule with meals and tracking columns."""
    days = []
    for day_num in range(1, duration_days + 1):
        week_num = (day_num - 1) // 7 + 1
        if week_num > 4:
            week_num = 4  # days 29-30 still in week 4
        phase = WEEK_PHASES[min(week_num, 4)]["name"]

        # Pick meals with some variety
        breakfast = rng.choice(BREAKFASTS)
        lunch = rng.choice(LUNCHES)
        dinner = rng.choice(DINNERS)

        # Daily focus: week 1 gets specific items, rest get default
        if week_num == 1 and (day_num - 1) < len(WEEK1_DAILY_FOCUS):
            daily_focus = WEEK1_DAILY_FOCUS[day_num - 1]
        else:
            daily_focus = DEFAULT_DAILY_FOCUS

        days.append({
            "day": day_num,
            "week": week_num,
            "phase": phase,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "snacks": DEFAULT_SNACKS,
            "hydration": DEFAULT_HYDRATION,
            "daily_focus": daily_focus,
        })

    return days


def _build_weeks() -> list:
    """Build Week 1-4 data with goals, shopping, meal prep, check-in."""
    weeks = []
    for week_num in range(1, 5):
        phase_info = WEEK_PHASES[week_num]
        weeks.append({
            "number": week_num,
            "title": f"Week {week_num}: {phase_info['name']}",
            "goals": phase_info["goals"],
            "shopping_list": SHOPPING_LIST,
            "meal_prep": MEAL_PREP,
            "check_in_questions": CHECK_IN_QUESTIONS,
        })
    return weeks


def print_schedule_summary(schedule: dict):
    """Print a human-readable schedule summary."""
    print("\n" + "=" * 60)
    print(f"  INTERVENTION SCHEDULE: {schedule['patient_name']}")
    print(f"  Duration: {schedule['plan_duration_days']} days")
    print(f"  {schedule['start_date']} \u2192 {schedule['end_date']}")
    print("=" * 60)

    print("\n  CORE PRINCIPLES:")
    for p in schedule["core_principles"]:
        print(f"    \u2713 {p}")

    print("\n  MILESTONES:")
    for ms in schedule["milestones"]:
        print(f"    Day {ms['day']:>2}: {ms['checkpoint']} \u2014 {ms['actions']}")

    print(f"\n  DAILY SCHEDULE: {len(schedule['daily_schedule'])} days")
    for day in schedule["daily_schedule"][:3]:
        print(f"    Day {day['day']:>2} (W{day['week']}) {day['phase']}: "
              f"{day['breakfast']} | {day['lunch']} | {day['dinner']}")
    print("    ...")

    print("\n  WEEKS:")
    for wk in schedule["weeks"]:
        print(f"\n    {wk['title']}")
        for g in wk["goals"]:
            print(f"      \u2610 {g}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Demo
    sample_data = {
        "fullName": "Demo Patient",
        "smokingStatus": "Current smoker",
        "exerciseFrequency": "Rarely",
        "dietQuality": "Fair",
        "stressLevel": "High",
    }
    risks = {"cardiovascular": 60, "metabolic": 40, "mental_health": 70, "respiratory": 50, "musculoskeletal": 20}
    schedule = generate_intervention_schedule(sample_data, risks, duration_days=30)
    print_schedule_summary(schedule)
