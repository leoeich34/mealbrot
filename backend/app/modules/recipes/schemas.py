from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.modules.catalog.schemas import IngredientRead


MealSlot = Literal["breakfast", "lunch", "dinner"]


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0)


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=220)
    description: str | None = None
    steps: str = Field(min_length=1)
    cooking_time: int = Field(gt=0)
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    calories: int | None = None
    meal_type: MealSlot = "dinner"
    image_url: HttpUrl | str | None = None
    ingredients: list[RecipeIngredientCreate] = Field(min_length=1)


class RecipeIngredientRead(BaseModel):
    ingredient: IngredientRead
    quantity: float

    model_config = ConfigDict(from_attributes=True)


class MissingIngredientRead(BaseModel):
    ingredient: IngredientRead
    required_quantity: float
    available_quantity: float
    missing_quantity: float
    estimated_cost: float | None


class RecipeRead(BaseModel):
    id: int
    title: str
    description: str | None
    steps: str
    cooking_time: int
    difficulty: str
    calories: int | None
    meal_type: str
    image_url: str | None
    ingredients: list[RecipeIngredientRead]
    can_cook: bool | None = None
    missing_ingredients: list[MissingIngredientRead] = []
    missing_cost: float | None = None

    model_config = ConfigDict(from_attributes=True)
