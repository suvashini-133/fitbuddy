import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
FLASH_MODEL_NAME = os.getenv("NUTRITION_MODEL", "gemini-1.5-flash")

flash_model = None
genai_client = None

if API_KEY:
    try:
        from google import genai
        genai_client = genai.Client(api_key=API_KEY)
    except Exception:
        try:
            import google.generativeai as gai
            gai.configure(api_key=API_KEY)
            flash_model = gai.GenerativeModel(FLASH_MODEL_NAME)
        except Exception:
            pass


def _fallback_nutrition_tip(goal: str) -> str:
    g = goal.lower()
    if "loss" in g or "fat" in g or "weight" in g:
        return (
            "Prioritize lean protein (like grilled chicken breast, lentils, eggs, and tofu) "
            "with every meal to maintain muscle and curb hunger. Pair with high-fiber greens "
            "and drink at least 2.5 to 3 liters of water daily to keep your metabolic rate optimal!"
        )
    elif "muscle" in g or "gain" in g or "bulk" in g:
        return (
            "Target 1.6 to 2.2 grams of protein per kilogram of body weight spread across 4-5 meals. "
            "Consume a carbohydrate and protein-rich snack (such as Greek yogurt with berries or a whey shake with banana) "
            "within 45 minutes post-workout to accelerate glycogen replenishment and muscle protein synthesis."
        )
    elif "flexib" in g or "mobility" in g or "yoga" in g:
        return (
            "Support joint health and tissue elasticity by staying thoroughly hydrated and eating foods rich in "
            "Omega-3 fatty acids (salmon, walnuts, chia seeds). Include magnesium-rich foods like spinach and pumpkin seeds "
            "in the evening to assist deep muscle relaxation."
        )
    else:
        return (
            "Focus on colorful, nutrient-dense whole foods: balance your plate with 1/2 vegetables and fruit, "
            "1/4 complex carbohydrates (sweet potatoes, brown rice), and 1/4 clean protein. "
            "Consistency in hydration and whole-food nutrition is the foundation of lasting vitality!"
        )


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """Generate a concise, practical nutrition or recovery tip tailored to user's fitness goal using Gemini Flash."""
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, scientifically grounded, and easy to understand (2-3 sentences)."
    )

    if genai_client:
        for model_candidate in [FLASH_MODEL_NAME, "gemini-2.5-flash", "gemini-1.5-flash"]:
            try:
                response = genai_client.models.generate_content(
                    model=model_candidate,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue

    if flash_model:
        try:
            response = flash_model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass

    return _fallback_nutrition_tip(goal)
