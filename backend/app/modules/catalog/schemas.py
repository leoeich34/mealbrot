from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Unit = Literal["g", "ml", "pcs"]


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
