from datetime import date

from pydantic import BaseModel, Field

from app.modules.catalog.schemas import CategoryRead, IngredientRead, Unit


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
