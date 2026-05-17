from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Category,
    Ingredient,
    InventoryItem,
    MealPlanEntry,
    Price,
    Recipe,
    RecipeIngredient,
    ShoppingListItem,
    User,
)
from app.shared.serializers import serialize_category, serialize_ingredient


MEAL_SLOTS = ("breakfast", "lunch", "dinner")


def expiration_status(expiration_date: date | None, today: date | None = None) -> str:
    if expiration_date is None:
        return "unknown"
    current = today or date.today()
    if expiration_date < current:
        return "expired"
    if expiration_date <= current + timedelta(days=3):
        return "soon"
    return "fresh"


def inventory_totals(db: Session, user: User) -> dict[int, float]:
    totals: dict[int, float] = defaultdict(float)
    items = db.scalars(
        select(InventoryItem).where(InventoryItem.user_id == user.id)
    ).all()
    for item in items:
        if expiration_status(item.expiration_date) != "expired":
            totals[item.ingredient_id] += item.quantity
    return dict(totals)


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


def generate_shopping_items(db: Session, user: User, start_date: date, days: int):
    entries = planned_entries(db, user, start_date, days)
    required: dict[int, float] = defaultdict(float)
    ingredient_by_id: dict[int, Ingredient] = {}
    for entry in entries:
        for recipe_item in entry.recipe.ingredients:
            required[recipe_item.ingredient_id] += recipe_item.quantity
            ingredient_by_id[recipe_item.ingredient_id] = recipe_item.ingredient

    available = inventory_totals(db, user)
    old_auto_items = db.scalars(
        select(ShoppingListItem).where(
            ShoppingListItem.user_id == user.id, ShoppingListItem.source == "auto"
        )
    ).all()
    for item in old_auto_items:
        db.delete(item)
    db.flush()

    created = []
    for ingredient_id, required_quantity in sorted(required.items()):
        missing_quantity = max(required_quantity - available.get(ingredient_id, 0.0), 0.0)
        if missing_quantity <= 0:
            continue
        ingredient = ingredient_by_id[ingredient_id]
        item = ShoppingListItem(
            user_id=user.id,
            ingredient_id=ingredient.id,
            title=ingredient.name,
            quantity=missing_quantity,
            unit=ingredient.unit,
            source="auto",
        )
        db.add(item)
        created.append(item)
    db.commit()
    for item in created:
        db.refresh(item)
    return created


def serialize_shopping_item(item: ShoppingListItem) -> dict:
    ingredient = item.ingredient
    return {
        "id": item.id,
        "title": item.title,
        "quantity": item.quantity,
        "unit": item.unit,
        "is_purchased": item.is_purchased,
        "source": item.source,
        "ingredient": serialize_ingredient(ingredient) if ingredient else None,
        "category": serialize_category(ingredient.category) if ingredient else None,
    }


def category_exists(db: Session, name: str) -> bool:
    return (
        db.scalar(select(func.count()).select_from(Category).where(Category.name == name))
        or 0
    ) > 0
