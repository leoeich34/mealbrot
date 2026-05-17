from datetime import date

from pydantic import BaseModel, ConfigDict

from app.modules.recipes.schemas import MealSlot, RecipeRead


class GenerateWeekRequest(BaseModel):
    start_date: date


class DayEntryCreate(BaseModel):
    meal_slot: MealSlot
    recipe_id: int


class DayUpdateRequest(BaseModel):
    entries: list[DayEntryCreate]


class MealPlanEntryRead(BaseModel):
    id: int
    planned_date: date
    meal_slot: str
    recipe: RecipeRead

    model_config = ConfigDict(from_attributes=True)


class PlannerResponse(BaseModel):
    entries: list[MealPlanEntryRead]


class DayResponse(BaseModel):
    date: date
    entries: list[MealPlanEntryRead]
