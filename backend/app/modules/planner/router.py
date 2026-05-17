from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MealPlanEntry, Recipe, User
from app.modules.planner.schemas import DayResponse, DayUpdateRequest, GenerateWeekRequest, PlannerResponse
from app.modules.planner.service import generate_week_plan, planned_entries
from app.security import get_current_user
from app.shared.crud import get_or_404


router = APIRouter()
@router.post("/planner/generate-week", response_model=PlannerResponse)
def generate_week(
    payload: GenerateWeekRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    generate_week_plan(db, user, payload.start_date)
    return {"entries": planned_entries(db, user, payload.start_date, 7)}

@router.get("/planner/month/{year}/{month}", response_model=PlannerResponse)
def get_month_plan(
    year: int,
    month: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start = date(year, month, 1)
    if month == 12:
        days = (date(year + 1, 1, 1) - start).days
    else:
        days = (date(year, month + 1, 1) - start).days
    return {"entries": planned_entries(db, user, start, days)}

@router.get("/planner/day/{planned_date}", response_model=DayResponse)
def get_day(
    planned_date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"date": planned_date, "entries": planned_entries(db, user, planned_date, 1)}

@router.put("/planner/day/{planned_date}", response_model=DayResponse)
def update_day(
    planned_date: date,
    payload: DayUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.scalars(
        select(MealPlanEntry).where(
            MealPlanEntry.user_id == user.id, MealPlanEntry.planned_date == planned_date
        )
    ).all()
    for entry in existing:
        db.delete(entry)
    db.flush()
    for entry in payload.entries:
        get_or_404(db, Recipe, entry.recipe_id)
        db.add(
            MealPlanEntry(
                user_id=user.id,
                recipe_id=entry.recipe_id,
                planned_date=planned_date,
                meal_slot=entry.meal_slot,
            )
        )
    db.commit()
    return {"date": planned_date, "entries": planned_entries(db, user, planned_date, 1)}
