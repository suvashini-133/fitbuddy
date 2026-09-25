import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Float, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/fitbuddy.db")

# Parse SQLite file path to ensure parent directory exists
if DATABASE_URL.startswith("sqlite:///"):
    db_relative_path = DATABASE_URL.replace("sqlite:///", "")
    db_path = Path(db_relative_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
else:
    Path("./data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    schedule = Column(Integer, default=7)


class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(
    user_id: int,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
):
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            user = User(
                id=user_id,
                name=name,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
                schedule=7,
            )
            db.add(user)
        db.commit()
    finally:
        db.close()


def save_plan(user_id: int, plan: str):
    db = SessionLocal()
    try:
        existing = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if existing:
            existing.original_plan = plan
        else:
            workout = WorkoutPlan(user_id=user_id, original_plan=plan)
            db.add(workout)
        db.commit()
    finally:
        db.close()


def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()
    finally:
        db.close()


def get_original_plan(user_id: int):
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None
    finally:
        db.close()


def get_user_plan(user_id: int):
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    finally:
        db.close()


def get_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def get_all_plans():
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).all()
    finally:
        db.close()


def delete_user_data(user_id: int):
    db = SessionLocal()
    try:
        db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).delete()
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
    finally:
        db.close()
