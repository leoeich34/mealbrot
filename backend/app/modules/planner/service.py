from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Ingredient, MealPlanEntry, Recipe, RecipeIngredient, User
from app.modules.recipes.service import (
    load_recipes_query,
    recipe_analysis,
    recipe_is_allowed_for_user,
)


MEAL_SLOTS = ("breakfast", "lunch", "dinner")


def choose_recipe_for_slot(db: Session, user: User, slot: str, budget_left: float | None):
    recipes = db.scalars(
        load_recipes_query().where(Recipe.meal_type == slot).order_by(Recipe.cooking_time.asc())
    ).unique().all()
    if not recipes:
        recipes = db.scalars(load_recipes_query().order_by(Recipe.cooking_time.asc())).unique().all()

    best = None
    best_cost = None
    for recipe in recipes:
        if not recipe_is_allowed_for_user(recipe, user):
            continue
        analysis = recipe_analysis(db, recipe, user)
        cost = analysis["missing_cost"]
        sortable_cost = cost if cost is not None else 10**9
        if budget_left is not None and cost is not None and cost > budget_left:
            continue
        if best is None or sortable_cost < best_cost:
            best = recipe
            best_cost = sortable_cost
    return best, None if best_cost == 10**9 else best_cost


def generate_week_plan(db: Session, user: User, start_date: date) -> list[MealPlanEntry]:
    end_date = start_date + timedelta(days=7)
    existing = db.scalars(
        select(MealPlanEntry).where(
            MealPlanEntry.user_id == user.id,
            MealPlanEntry.planned_date >= start_date,
            MealPlanEntry.planned_date < end_date,
        )
    ).all()
    for item in existing:
        db.delete(item)
    db.flush()

    entries = []
    budget_left = user.weekly_budget
    for offset in range(7):
        planned_date = start_date + timedelta(days=offset)
        for slot in MEAL_SLOTS:
            recipe, cost = choose_recipe_for_slot(db, user, slot, budget_left)
            if not recipe:
                continue
            if budget_left is not None and cost is not None:
                budget_left -= cost
            entry = MealPlanEntry(
                user_id=user.id,
                recipe_id=recipe.id,
                planned_date=planned_date,
                meal_slot=slot,
            )
            db.add(entry)
            entries.append(entry)
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return entries


def planned_entries(db: Session, user: User, start_date: date, days: int):
    end_date = start_date + timedelta(days=days)
    return db.scalars(
        select(MealPlanEntry)
        .options(
            joinedload(MealPlanEntry.recipe)
            .joinedload(Recipe.ingredients)
            .joinedload(RecipeIngredient.ingredient)
            .joinedload(Ingredient.category)
        )
        .where(
            MealPlanEntry.user_id == user.id,
            MealPlanEntry.planned_date >= start_date,
            MealPlanEntry.planned_date < end_date,
        )
        .order_by(MealPlanEntry.planned_date.asc(), MealPlanEntry.meal_slot.asc())
    ).unique().all()
