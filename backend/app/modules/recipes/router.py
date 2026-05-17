from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipe, User
from app.modules.recipes.schemas import RecipeRead
from app.modules.recipes.service import load_recipes_query, recipe_analysis
from app.security import get_current_user


router = APIRouter()
@router.get("/recipes", response_model=list[RecipeRead])
def list_recipes(
    q: str | None = None,
    meal_type: str | None = None,
    difficulty: str | None = None,
    max_time: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = load_recipes_query().order_by(Recipe.title.asc())
    if q:
        query = query.where(Recipe.title.ilike(f"%{q}%"))
    if meal_type:
        query = query.where(Recipe.meal_type == meal_type)
    if difficulty:
        query = query.where(Recipe.difficulty == difficulty)
    if max_time:
        query = query.where(Recipe.cooking_time <= max_time)
    recipes = db.scalars(query).unique().all()
    return [recipe_analysis(db, recipe, user) for recipe in recipes]
