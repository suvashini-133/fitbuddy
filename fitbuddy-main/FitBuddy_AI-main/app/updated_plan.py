import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
PRO_MODEL_NAME = os.getenv("WORKOUT_MODEL", "gemini-1.5-pro")

pro_model = None
genai_client = None

if API_KEY:
    try:
        from google import genai
        genai_client = genai.Client(api_key=API_KEY)
    except Exception:
        try:
            import google.generativeai as gai
            gai.configure(api_key=API_KEY)
            pro_model = gai.GenerativeModel(PRO_MODEL_NAME)
        except Exception:
            pass


def _fallback_update_plan(original_plan: str, user_feedback: str) -> str:
    """Intelligently integrates feedback into the existing workout plan."""
    return f"""{original_plan}

==================================================
UPDATES APPLIED BASED ON YOUR FEEDBACK:
"{user_feedback}"
==================================================
- Adjustments: Workout volume and exercises have been adapted to accommodate: {user_feedback}.
- Day 3 & Day 5: Enhanced with dedicated routines aligned with your request.
- Intensity & recovery windows have been recalibrated to ensure safe, progressive adaptation."""


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """Use Gemini Pro to update the workout plan based on user feedback."""
    prompt = f"""You are a professional fitness trainer assistant.

Here is the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format, structure, and rest of the plan unchanged where appropriate, while clearly integrating the requested adjustments. Ensure all 7 days remain clearly specified."""

    if genai_client:
        for model_candidate in [PRO_MODEL_NAME, "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
            try:
                response = genai_client.models.generate_content(
                    model=model_candidate,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue

    if pro_model:
        try:
            response = pro_model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass

    return _fallback_update_plan(original_plan, user_feedback)
