from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Ingredient, Price, Recipe, RecipeIngredient, User
from app.modules.inventory.service import inventory_totals
from app.shared.serializers import serialize_ingredient


def cheapest_price(db: Session, ingredient_id: int) -> Price | None:
    return db.scalar(
        select(Price)
        .where(Price.ingredient_id == ingredient_id)
        .order_by(Price.price_per_unit.asc())
        .limit(1)
    )


def estimate_cost(db: Session, ingredient: Ingredient, quantity: float) -> float | None:
    price = cheapest_price(db, ingredient.id)
    if price is None:
        return None
    if ingredient.unit in {"g", "ml"}:
        return round((quantity / 1000) * price.price_per_unit, 2)
    return round(quantity * price.price_per_unit, 2)


def recipe_analysis(db: Session, recipe: Recipe, user: User | None = None) -> dict:
    totals = inventory_totals(db, user) if user else {}
    missing = []
    missing_cost = 0.0
    has_unknown_price = False
    ingredients = []

    for recipe_item in recipe.ingredients:
        ingredient = recipe_item.ingredient
        ingredients.append(
            {"ingredient": serialize_ingredient(ingredient), "quantity": recipe_item.quantity}
        )
        available = totals.get(ingredient.id, 0.0)
        missing_quantity = max(recipe_item.quantity - available, 0.0)
        if missing_quantity > 0:
            cost = estimate_cost(db, ingredient, missing_quantity)
            if cost is None:
                has_unknown_price = True
            else:
                missing_cost += cost
            missing.append(
                {
                    "ingredient": serialize_ingredient(ingredient),
                    "required_quantity": recipe_item.quantity,
                    "available_quantity": available,
                    "missing_quantity": missing_quantity,
                    "estimated_cost": cost,
                }
            )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "steps": recipe.steps,
        "cooking_time": recipe.cooking_time,
        "difficulty": recipe.difficulty,
        "calories": recipe.calories,
        "meal_type": recipe.meal_type,
        "image_url": recipe.image_url,
        "ingredients": ingredients,
        "can_cook": not missing,
        "missing_ingredients": missing,
        "missing_cost": None if has_unknown_price and missing_cost == 0 else round(missing_cost, 2),
    }


def load_recipes_query():
    return select(Recipe).options(
        joinedload(Recipe.ingredients)
        .joinedload(RecipeIngredient.ingredient)
        .joinedload(Ingredient.category)
    )


def recipe_is_allowed_for_user(recipe: Recipe, user: User) -> bool:
    allergy_text = (user.allergies or "").lower()
    if not allergy_text.strip():
        return True
    blocked_words = [part.strip() for part in allergy_text.replace(",", ";").split(";")]
    haystack = " ".join(
        [recipe.title.lower()]
        + [item.ingredient.name.lower() for item in recipe.ingredients]
    )
    return not any(word and word in haystack for word in blocked_words)
