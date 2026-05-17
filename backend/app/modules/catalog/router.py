from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Category, Ingredient, Store, User
from app.modules.catalog.schemas import CategoryRead, IngredientRead, StoreRead
from app.security import get_current_user


router = APIRouter()
@router.get("/catalog/categories", response_model=list[CategoryRead])
def catalog_categories(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.scalars(
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.name.asc())
    ).all()

@router.get("/catalog/ingredients", response_model=list[IngredientRead])
def catalog_ingredients(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.scalars(
        select(Ingredient)
        .options(joinedload(Ingredient.category))
        .join(Ingredient.category)
        .where(Category.is_active.is_(True))
        .order_by(Ingredient.name.asc())
    ).all()

@router.get("/catalog/stores", response_model=list[StoreRead])
def catalog_stores(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Store).where(Store.is_active.is_(True)).order_by(Store.name.asc())
    ).all()
