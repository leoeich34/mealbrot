from app.models import Ingredient


def serialize_category(category):
    return {"id": category.id, "name": category.name, "is_active": category.is_active}


def serialize_ingredient(ingredient: Ingredient) -> dict:
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "unit": ingredient.unit,
        "category": serialize_category(ingredient.category),
    }
