from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


Unit = Literal["g", "ml", "pcs"]
MealSlot = Literal["breakfast", "lunch", "dinner"]


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    is_active: bool = True


class CategoryRead(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    unit: Unit
    category_id: int


class IngredientRead(BaseModel):
    id: int
    name: str
    unit: Unit
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)


class StoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    is_active: bool = True


class StoreRead(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PriceCreate(BaseModel):
    ingredient_id: int
    store_id: int
    price_per_unit: float = Field(gt=0)


class PriceRead(BaseModel):
    id: int
    ingredient: IngredientRead
    store: StoreRead
    price_per_unit: float

    model_config = ConfigDict(from_attributes=True)


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


class InventoryCreate(BaseModel):
    ingredient_id: int
    quantity: float = Field(gt=0)
    expiration_date: date | None = None


class InventoryRead(BaseModel):
    id: int
    ingredient: IngredientRead
    quantity: float
    expiration_date: date | None
    expiration_status: str


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


class ShoppingGenerateRequest(BaseModel):
    start_date: date
    days: int = Field(default=7, ge=1, le=31)


class ShoppingItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    quantity: float = Field(gt=0)
    unit: Unit
    ingredient_id: int | None = None


class ShoppingItemPatch(BaseModel):
    is_purchased: bool


class ShoppingItemRead(BaseModel):
    id: int
    title: str
    quantity: float
    unit: str
    is_purchased: bool
    source: str
    ingredient: IngredientRead | None = None
    category: CategoryRead | None = None


class ShoppingListResponse(BaseModel):
    items: list[ShoppingItemRead]
