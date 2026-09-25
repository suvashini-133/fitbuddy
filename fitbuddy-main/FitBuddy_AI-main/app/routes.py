import os
from pathlib import Path
from fastapi import APIRouter, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import (
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_user_plan,
    get_all_users,
    get_all_plans,
    delete_user_data,
)
from app.schemas import (
    UserInput,
    WorkoutRequest,
    FeedbackRequest,
    WorkoutResponse,
    NutritionResponse,
    PlanGenerationResponse,
    PlanUpdateResponse,
)
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

# Resolve templates directory (handles running from project root or inside app)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter()


# =====================================================================
# HTML Web Routes
# =====================================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the user input form homepage."""
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    """Process user form input, generate workout & nutrition tip, save to DB, and render result."""
    user_data = UserInput(
        username=username.strip(),
        user_id=user_id,
        age=age,
        weight=weight,
        goal=goal.strip(),
        intensity=intensity.strip(),
    )

    # Call Gemini Pro for 7-day workout plan
    workout_plan = generate_workout_gemini({
        "goal": user_data.goal,
        "intensity": user_data.intensity,
    })

    # Call Gemini Flash for nutrition tip
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    # Save user and initial plan to database
    save_user(
        user_id=user_data.user_id,
        name=user_data.username,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity,
    )
    save_plan(user_id=user_data.user_id, plan=workout_plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": user_data.username,
            "user_id": user_data.user_id,
            "age": user_data.age,
            "weight": user_data.weight,
            "goal": user_data.goal,
            "intensity": user_data.intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": None,
            "feedback_success": False,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
):
    """Retrieve existing plan, update using Gemini Pro based on user feedback, save update, and render result."""
    user = get_user(user_id)
    original_plan = get_original_plan(user_id)

    if not original_plan:
        # If user not found, render result with friendly error
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "username": user.name if user else f"User #{user_id}",
                "user_id": user_id,
                "age": user.age if user else "-",
                "weight": user.weight if user else "-",
                "goal": user.goal if user else "-",
                "intensity": user.intensity if user else "-",
                "workout_plan": "No existing workout plan found for this User ID. Please generate a plan first from the home page.",
                "nutrition_tip": "Stay consistent and properly hydrate daily.",
                "updated_plan": None,
                "feedback_success": False,
                "error_message": f"User ID {user_id} was not found in the database. Please generate an initial plan first.",
            },
        )

    # Update plan via Gemini Pro
    updated_plan_text = update_workout_plan(original_plan, feedback)
    update_plan(user_id, updated_plan_text)

    # Fetch nutrition tip
    goal = user.goal if user else "General Fitness"
    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": user.name if user else f"User #{user_id}",
            "user_id": user_id,
            "age": user.age if user else "-",
            "weight": user.weight if user else "-",
            "goal": user.goal if user else "-",
            "intensity": user.intensity if user else "-",
            "workout_plan": original_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": updated_plan_text,
            "feedback_success": True,
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request):
    """Admin view: Displays all registered users and their original & updated plans in a table."""
    users = get_all_users()
    plans = get_all_plans()

    # Map plans by user_id
    plan_map = {p.user_id: p for p in plans}

    user_data = []
    for u in users:
        p = plan_map.get(u.id)
        user_data.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "original_plan": p.original_plan if (p and p.original_plan) else "N/A",
            "updated_plan": p.updated_plan if (p and p.updated_plan) else "Not updated",
        })

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": user_data},
    )


@router.post("/delete-user/{user_id}")
async def delete_user(user_id: int):
    """Admin action to delete a user and their workout plan records."""
    delete_user_data(user_id)
    return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)


# =====================================================================
# REST API Endpoints (as defined in PDF Milestone 3)
# =====================================================================

@router.post(
    "/generate-workout/gemini",
    response_model=WorkoutResponse,
    summary="Generate workout using Gemini Pro",
)
async def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({
            "goal": request.goal,
            "intensity": request.intensity,
        })
        return WorkoutResponse(model="gemini-pro", workout_plan=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/nutrition-tip",
    response_model=NutritionResponse,
    summary="Generate nutrition tip using Gemini Flash",
)
def get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return NutritionResponse(goal=goal, nutrition_tip=tip)


@router.post(
    "/generate-plan",
    response_model=PlanGenerationResponse,
    summary="Save user info & generate plan",
)
def api_generate_plan(user_data: UserInput):
    try:
        save_user(
            user_id=user_data.user_id,
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )
        plan = generate_workout_gemini({
            "goal": user_data.goal,
            "intensity": user_data.intensity,
        })
        save_plan(user_data.user_id, plan)
        return PlanGenerationResponse(
            message="Workout plan generated and saved successfully!",
            workout_plan=plan,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


@router.post(
    "/update-plan/{user_id}",
    response_model=PlanUpdateResponse,
    summary="Update workout plan based on user feedback",
)
def api_update_user_plan(user_id: int, data: FeedbackRequest):
    original = get_original_plan(user_id)
    if not original:
        raise HTTPException(
            status_code=404,
            detail=f"Original plan not found for user ID {user_id}",
        )
    updated = update_workout_plan(original, data.feedback)
    update_plan(user_id, updated)
    return PlanUpdateResponse(updated_plan=updated)