from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, ShoppingListItem, User
from app.modules.inventory.service import inventory_totals
from app.modules.planner.service import planned_entries
from app.shared.serializers import serialize_category, serialize_ingredient


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
