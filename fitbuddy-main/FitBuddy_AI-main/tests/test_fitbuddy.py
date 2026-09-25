import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import (
    init_db,
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_all_users,
    delete_user_data,
)
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    # Clean test user if exists
    delete_user_data(999)
    yield
    delete_user_data(999)


def test_database_crud():
    # 1. Save user
    save_user(
        user_id=999,
        name="Test Athlete",
        age=28,
        weight=75.5,
        goal="Muscle Gain",
        intensity="High",
    )
    user = get_user(999)
    assert user is not None
    assert user.name == "Test Athlete"
    assert user.weight == 75.5

    # 2. Save plan
    save_plan(user_id=999, plan="Day 1: Upper Body Strength")
    plan = get_original_plan(999)
    assert plan == "Day 1: Upper Body Strength"

    # 3. Update plan
    update_plan(user_id=999, updated_text="Day 1: Upper Body + Added Cardio")
    user_plan = get_original_plan(999)
    assert user_plan == "Day 1: Upper Body Strength"

    # 4. Get all users
    users = get_all_users()
    assert any(u.id == 999 for u in users)

    # 5. Delete
    delete_user_data(999)
    assert get_user(999) is None


def test_ai_generators():
    # Workout Generator
    workout = generate_workout_gemini({"goal": "Fat Loss", "intensity": "High"})
    assert isinstance(workout, str)
    assert len(workout) > 50

    # Nutrition Generator
    tip = generate_nutrition_tip_with_flash("Muscle Gain")
    assert isinstance(tip, str)
    assert len(tip) > 20

    # Update Generator
    revised = update_workout_plan("Original Routine", "Add more cardio")
    assert isinstance(revised, str)
    assert len(revised) > 20


def test_web_routes():
    # 1. Homepage GET
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert "FitBuddy" in res_home.text
    assert "Generate Plan" in res_home.text

    # 2. Form submission /generate-workout
    form_data = {
        "username": "Test Athlete",
        "user_id": 999,
        "age": 28,
        "weight": 75.5,
        "goal": "Weight Loss",
        "intensity": "Medium",
    }
    res_gen = client.post("/generate-workout", data=form_data)
    assert res_gen.status_code == 200
    assert "Your Personalized Workout Plan" in res_gen.text
    assert "Test Athlete" in res_gen.text

    # 3. Submit feedback /submit-feedback
    fb_data = {
        "user_id": 999,
        "feedback": "Please add more stretching and foam rolling to Day 4.",
    }
    res_fb = client.post("/submit-feedback", data=fb_data)
    assert res_fb.status_code == 200
    assert "Your plan has been updated based on your feedback!" in res_fb.text

    # 4. Admin View /view-all-users
    res_admin = client.get("/view-all-users")
    assert res_admin.status_code == 200
    assert "Test Athlete" in res_admin.text
    assert "#999" in res_admin.text


def test_rest_api_endpoints():
    # 1. /generate-workout/gemini
    res1 = client.post(
        "/generate-workout/gemini",
        json={"goal": "Cardio Endurance", "intensity": "Medium"},
    )
    assert res1.status_code == 200
    json1 = res1.json()
    assert json1["model"] == "gemini-pro"
    assert "workout_plan" in json1

    # 2. /nutrition-tip
    res2 = client.get("/nutrition-tip?goal=Muscle%20Gain")
    assert res2.status_code == 200
    json2 = res2.json()
    assert json2["goal"] == "Muscle Gain"
    assert "nutrition_tip" in json2

    # 3. /generate-plan
    res3 = client.post(
        "/generate-plan",
        json={
            "username": "API Tester",
            "user_id": 999,
            "age": 30,
            "weight": 80.0,
            "goal": "General Fitness",
            "intensity": "Low",
        },
    )
    assert res3.status_code == 200
    json3 = res3.json()
    assert "Workout plan generated and saved successfully!" in json3["message"]

    # 4. /update-plan/{user_id}
    res4 = client.post(
        "/update-plan/999",
        json={"feedback": "Add 10 minutes of yoga."},
    )
    assert res4.status_code == 200
    assert "updated_plan" in res4.json()
