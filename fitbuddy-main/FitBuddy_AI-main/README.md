# 🏋️ FitBuddy – AI Fitness Plan Generator

FitBuddy is an intelligent, web-based fitness planning application powered by **FastAPI**, **SQLite (via SQLAlchemy ORM)**, and **Google Gemini AI models**. It generates customized 7-day workout routines and tailored nutrition advice based on individual user profiles, accepts interactive feedback to dynamically revise plans, and provides a dedicated admin dashboard for monitoring user fitness plans.

---

## 🌟 Key Features

- **Personalized 7-Day Workout Plans**: Generates structured, day-by-day training routines containing warm-ups (5–10 mins), targeted main exercises (sets & reps), and cooldowns aligned with the user's fitness goal and chosen intensity.
- **Goal-Aligned Nutrition & Recovery Tips**: Leverages lightweight, fast AI generation to deliver concise dietary guidance (e.g., protein targets, hydration, meal timing, and restorative practices).
- **Dynamic Feedback Loop**: Enables users to submit feedback (e.g., *"add more cardio"*, *"more rest days"*, *"knee-friendly modifications"*) to revise their existing workout plan while keeping the original structure intact.
- **SQLAlchemy ORM Data Persistence**: Stores user profiles, original workout plans, and updated plans in a local SQLite database (`data/fitbuddy.db`).
- **Interactive Web Interface & Admin Dashboard**: Responsive Jinja2-rendered HTML pages with custom gym aesthetics and an admin overview table showing all registered users and their evolving plans.
- **Dual Interface**: Supports both browser-based forms and full RESTful JSON API endpoints documented automatically with OpenAPI (Swagger UI).

---

## 🏗️ Technical Architecture

```text
                               ┌────────────────────────────────┐
                               │       User / Web Browser       │
                               └───────────────┬────────────────┘
                                               │
                                 HTTP Requests (Form / JSON)
                                               │
                                               ▼
                               ┌────────────────────────────────┐
                               │   FastAPI App (app/main.py)    │
                               │   Route Handlers (routes.py)   │
                               └───────┬──────────────┬─────────┘
                                       │              │
                   ┌───────────────────┴──┐        ┌──┴───────────────────┐
                   ▼                      ▼        ▼                      ▼
        ┌─────────────────────┐ ┌───────────────┐ ┌─────────────────┐ ┌───────────────┐
        │  Jinja2 Templates   │ │Pydantic Models│ │ SQLAlchemy ORM  │ │ Google Gemini │
        │ (index, result,     │ │ (schemas.py)  │ │ (database.py)   │ │  Pro & Flash  │
        │  all_users)         │ └───────────────┘ └────────┬────────┘ └───────────────┘
        └─────────────────────┘                            │
                                                           ▼
                                                ┌─────────────────────┐
                                                │ SQLite Database     │
                                                │ (data/fitbuddy.db)  │
                                                └─────────────────────┘
```

---

## 📂 Project Structure

```text
fitbuddy-ai/
├── app/
│   ├── __init__.py               # Application package marker
│   ├── main.py                   # FastAPI entrypoint, static files & lifespan
│   ├── routes.py                 # Core route handlers (Web & REST API)
│   ├── database.py               # SQLAlchemy ORM models & DB logic
│   ├── schemas.py                # Pydantic data validation schemas
│   ├── gemini_generator.py       # Gemini Pro: 7-day workout plan generation
│   ├── gemini_flash_generator.py # Gemini Flash: Concise nutrition tips
│   └── updated_plan.py           # Gemini Pro: Feedback-based plan reviser
├── templates/
│   ├── index.html                # Form page for user input
│   ├── result.html               # Plan display, nutrition tip & feedback form
│   └── all_users.html            # Admin panel to view & delete users
├── static/
│   ├── css/
│   │   └── style.css             # Responsive styling & modern fitness theme
│   └── images/
│       └── gym-bg.jpg            # Gym-themed background image asset
├── data/
│   └── fitbuddy.db               # SQLite database (auto-generated)
├── tests/
│   └── test_fitbuddy.py          # Pytest test suite for DB, AI & endpoints
├── .env                          # Environment variables & API keys
├── requirements.txt              # Python project dependencies
└── README.md                     # Documentation
```

---

## 🛠️ Tech Stack & Prerequisites

- **Python 3.10+** (Tested on Python 3.14)
- **FastAPI**: Asynchronous web framework for APIs and web routing.
- **Uvicorn**: Lightning-fast ASGI server.
- **SQLAlchemy & SQLite**: ORM and relational database storage.
- **Google Generative AI SDK** (`google-genai` / `google-generativeai`): Gemini 1.5/2.5 Pro & Flash models.
- **Jinja2**: Templating engine for HTML page rendering.
- **Pydantic v2**: Data validation and type enforcement.
- **Pytest**: Automated testing framework.

---

## 🚀 Getting Started

### 1. Clone or Open the Repository
```bash
cd "F:/saravanan project/fitbuddy-ai"
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or verify your `.env` file in the project root:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
WORKOUT_MODEL=gemini-1.5-pro
NUTRITION_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///./data/fitbuddy.db
APP_NAME=FitBuddy
```

> **Note:** The application includes a fallback system. If the Gemini API key is missing or hits quota limits during offline demos, the app provides realistic, goal-tailored workout plans and nutrition tips.

---

## 🏃 Running the Application

Start the local development server with Uvicorn:

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started, access the application in your browser:
- 🏋️ **Plan Generator (Homepage)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 📊 **Admin Dashboard**: [http://127.0.0.1:8000/view-all-users](http://127.0.0.1:8000/view-all-users)
- 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📋 Endpoints Overview

### Web Routes (HTML)
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Homepage displaying user information form (`index.html`) |
| `POST` | `/generate-workout` | Processes user form, generates workout & nutrition, saves to DB, renders `result.html` |
| `POST` | `/submit-feedback` | Updates workout plan based on user feedback and refreshes `result.html` |
| `GET` | `/view-all-users` | Admin dashboard listing all registered users & plan versions (`all_users.html`) |
| `POST` | `/delete-user/{user_id}` | Admin action to delete a user and their associated plans |

### REST API Endpoints (JSON)
| Method | Path | Request Body / Params | Description |
|---|---|---|---|
| `POST` | `/generate-workout/gemini` | `{"goal": "string", "intensity": "string"}` | Direct Gemini Pro workout generation |
| `GET` | `/nutrition-tip` | `?goal=string` | Direct Gemini Flash nutrition tip generation |
| `POST` | `/generate-plan` | `UserInput` JSON | Saves user and generates structured plan |
| `POST` | `/update-plan/{user_id}` | `{"feedback": "string"}` | Updates plan for specified user ID |

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:

```powershell
.\venv\Scripts\python.exe -m pytest tests -v
```

This verifies:
1. Database CRUD operations (`save_user`, `save_plan`, `update_plan`, `delete_user_data`).
2. AI generation logic (workout, nutrition, plan revision).
3. Web routes (`/`, `/generate-workout`, `/submit-feedback`, `/view-all-users`).
4. JSON REST API endpoints.

---

## 📄 License
This project was developed as part of the SmartBridge / SmartInternz Applied AI program.
