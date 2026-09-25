from typing import Optional
from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(..., description="User's full name")
    user_id: int = Field(..., description="Unique User ID")
    age: int = Field(..., ge=1, le=120, description="User's age")
    weight: float = Field(..., ge=10.0, le=500.0, description="User's weight in kilograms")
    goal: str = Field(..., description="Fitness goal (e.g., Weight Loss, Muscle Gain, General Fitness)")
    intensity: str = Field(..., description="Preferred workout intensity (Low, Medium, High)")


class WorkoutRequest(BaseModel):
    goal: str = Field(..., description="Fitness goal")
    intensity: str = Field(..., description="Workout intensity: Low, Medium, High")


class FeedbackRequest(BaseModel):
    feedback: str = Field(..., description="User feedback to refine existing plan")


class WorkoutResponse(BaseModel):
    model: str
    workout_plan: str


class NutritionResponse(BaseModel):
    goal: str
    nutrition_tip: str


class PlanGenerationResponse(BaseModel):
    message: str
    workout_plan: str


class PlanUpdateResponse(BaseModel):
    updated_plan: str
