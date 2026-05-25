# Meal Planning and Recipe Service

Full-stack MVP for meal planning, recipe management, home inventory, and shopping list generation. The project shows backend/API design, relational data modeling, frontend workflows, and Docker-based local runtime.

## Scope

- User registration, login, logout, and profile flow.
- Role model with `admin` and `user`.
- Admin CRUD for categories, ingredients, stores, prices, recipes, and user roles.
- Home inventory with expiration-date status.
- Recipe matching with missing ingredient calculation and estimated cost.
- Monthly meal calendar with breakfast/lunch/dinner slots.
- Weekly auto-plan generation.
- Shopping list generation from the selected meal plan.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic, PyJWT.
- Frontend: Vue 3, Vite, Pinia, Vue Router, Tailwind CSS.
- Testing: pytest, Vitest, Vue Test Utils.
- Runtime: Docker, docker-compose, nginx config for deployment.

## Repository Structure

```text
backend/       FastAPI app, database models, migrations, seed data, tests
frontend/      Vue 3 app, routing, UI logic, frontend tests
deploy/        nginx configuration
docker-compose.yml
```

## Quick Start

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Prepare the backend:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
cp .env.example .env
DATABASE_URL=postgresql+psycopg://meal:meal@127.0.0.1:5432/meal_planner ../.venv/bin/alembic upgrade head
DATABASE_URL=postgresql+psycopg://meal:meal@127.0.0.1:5432/meal_planner ../.venv/bin/python -m app.seed
../.venv/bin/uvicorn app.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Seed admin account:

```text
admin@example.com / admin123
```

## Checks

Backend:

```bash
cd backend
../.venv/bin/python -m pytest -q
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Portfolio Note

This project is not a Data Science project; it is included as an engineering sample. It demonstrates API design, database-backed workflows, frontend state management, automated tests, and Dockerized local infrastructure.
