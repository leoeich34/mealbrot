from datetime import date

from pydantic import BaseModel, Field

from app.modules.catalog.schemas import IngredientRead


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
