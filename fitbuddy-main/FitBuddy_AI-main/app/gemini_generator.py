import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("WORKOUT_MODEL", "gemini-1.5-pro")

# Initialize client/model if available
gemini_model = None
genai_client = None

if API_KEY:
    try:
        from google import genai
        genai_client = genai.Client(api_key=API_KEY)
    except Exception:
        try:
            import google.generativeai as gai
            gai.configure(api_key=API_KEY)
            gemini_model = gai.GenerativeModel(MODEL_NAME)
        except Exception:
            pass


def _fallback_workout_plan(goal: str, intensity: str) -> str:
    """Provides a structured 7-day plan when live Gemini API is unreachable."""
    g = goal.lower()
    i = intensity.capitalize()
    return f"""## 7-Day {i} Intensity Workout Plan for {goal.title()}

**Goal:** {goal.title()} | **Intensity:** {i} | **Schedule:** 7 Days

---

### Day 1: Upper Body Strength & Posture Focus
* **Warm-up (7 mins):** Arm circles (60s), Jumping jacks (2 mins), Dynamic shoulder rotations (2 mins), Cat-cow stretch (2 mins)
* **Main Workout:**
  - Push-ups (or knee push-ups): 3 sets x 10-12 reps
  - Dumbbell / Resistance Band Rows: 3 sets x 12 reps
  - Overhead Shoulder Press: 3 sets x 10 reps
  - Plank Hold: 3 sets x 45 seconds
* **Cooldown (5 mins):** Static chest stretch, cross-body shoulder stretch, deep diaphragmatic breathing.

---

### Day 2: Lower Body Power & Core Foundation
* **Warm-up (8 mins):** Bodyweight squats (20 reps), Glute bridges (15 reps), Leg swings (60s each leg)
* **Main Workout:**
  - Goblet Squats or Bodyweight Squats: 4 sets x 12-15 reps
  - Romanian Deadlifts (Dumbbells/Band): 3 sets x 12 reps
  - Walking Lunges: 3 sets x 10 reps per leg
  - Hanging Knee Raises or Reverse Crunches: 3 sets x 15 reps
* **Cooldown (5 mins):** Hamstring fold, quad stretch against wall, pigeon pose.

---

### Day 3: Cardiovascular Conditioning & Core Blast
* **Warm-up (5 mins):** High knees in place (2 mins), Boxer shuffle (2 mins), Torso twists (1 min)
* **Main Workout:**
  - HIIT Circuit (30s work / 30s rest x 4 rounds):
    - Mountain Climbers
    - Jump Squats (or speed bodyweight squats)
    - Kettlebell / Dumbbell Swings
    - Russian Twists
  - Moderate Jog or Brisk Incline Walk: 15 minutes steady state
* **Cooldown (5 mins):** Child's pose, calf stretches, gentle forward bends.

---

### Day 4: Active Recovery & Mobility
* **Activity:** 30-40 minutes of restorative movement:
  - Low-intensity walk in nature or light cycling
  - Full-body mobility routine: Foam rolling quads, thoracic spine rotations, hip flexor stretches
* **Cooldown / Recovery Tip:** Drink 3L of water, practice mindful breathing, get 8 hours of sleep.

---

### Day 5: Full Body Functional Conditioning
* **Warm-up (6 mins):** Butt kicks (2 mins), Inchworms (6 reps), Arm cross-overs (2 mins)
* **Main Workout:**
  - Dumbbell Thrusters (Squat to Press): 3 sets x 10-12 reps
  - Renegade Rows or Plank Shoulder Taps: 3 sets x 10 reps per side
  - Step-ups (onto box or bench): 3 sets x 12 reps per leg
  - Bicycle Crunches: 3 sets x 20 reps
* **Cooldown (5 mins):** Cobra stretch, seated forward bend, shoulder rolls.

---

### Day 6: Posterior Chain, Back & Arm Definition
* **Warm-up (7 mins):** Light jog in place (2 mins), Band pull-aparts (20 reps), Hip circles (2 mins)
* **Main Workout:**
  - Lat Pulldowns or Pull-up Negatives: 3 sets x 10-12 reps
  - Dumbbell Bicep Curls superset with Tricep Dips: 3 sets x 12 reps each
  - Lateral Deltoid Raises: 3 sets x 15 reps
  - Side Planks: 3 sets x 30 seconds per side
* **Cooldown (5 mins):** Standing tricep stretch, doorway pec stretch, wrist mobility.

---

### Day 7: Total Body Restoration & Reflection
* **Activity:** 30 minutes of gentle yoga or dedicated stretching routine:
  - Cat-cow, downward dog, thread the needle, supine spinal twists
* **Cooldown / Recovery Tip:** Review your weekly progress, prepare nutrition for next week, celebrate consistency!"""


def generate_workout_gemini(user_input: dict) -> str:
    """Generate a 7-day personalized workout plan using Gemini Pro."""
    goal = user_input.get("goal", "General Fitness")
    intensity = user_input.get("intensity", "Medium")

    prompt = f"""You are a professional certified fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of **{goal}**, and prefers **{intensity}** intensity workouts.

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)

Make the plan motivating, safe, and clearly formatted."""

    # 1. Try google.genai Client
    if genai_client:
        for model_candidate in [MODEL_NAME, "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
            try:
                response = genai_client.models.generate_content(
                    model=model_candidate,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue

    # 2. Try google.generativeai GenerativeModel
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception:
            pass

    # 3. Fallback when API key quota is exhausted or unreachable
    return _fallback_workout_plan(goal, intensity)
