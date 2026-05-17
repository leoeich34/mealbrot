from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Ingredient, ShoppingListItem, User
from app.modules.shopping.schemas import (
    ShoppingGenerateRequest,
    ShoppingItemCreate,
    ShoppingItemPatch,
    ShoppingItemRead,
    ShoppingListResponse,
)
from app.modules.shopping.service import generate_shopping_items, serialize_shopping_item
from app.security import get_current_user
from app.shared.crud import commit_refresh, get_or_404


router = APIRouter()
@router.get("/shopping-list", response_model=ShoppingListResponse)
def list_shopping_items(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    items = db.scalars(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.user_id == user.id)
        .order_by(ShoppingListItem.source.asc(), ShoppingListItem.title.asc())
    ).all()
    return {"items": [serialize_shopping_item(item) for item in items]}

@router.post("/shopping-list/generate", response_model=ShoppingListResponse)
def generate_shopping_list(
    payload: ShoppingGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    generate_shopping_items(db, user, payload.start_date, payload.days)
    return list_shopping_items(user, db)

@router.post(
    "/shopping-list", response_model=ShoppingItemRead, status_code=status.HTTP_201_CREATED
)
def create_shopping_item(
    payload: ShoppingItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ingredient = (
        get_or_404(db, Ingredient, payload.ingredient_id)
        if payload.ingredient_id is not None
        else None
    )
    item = ShoppingListItem(
        user_id=user.id,
        ingredient_id=ingredient.id if ingredient else None,
        title=payload.title.strip(),
        quantity=payload.quantity,
        unit=payload.unit,
        source="manual",
    )
    commit_refresh(db, item)
    item = db.scalar(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.id == item.id)
    )
    return serialize_shopping_item(item)

@router.patch("/shopping-list/{item_id}", response_model=ShoppingItemRead)
def patch_shopping_item(
    item_id: int,
    payload: ShoppingItemPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, ShoppingListItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    item.is_purchased = payload.is_purchased
    commit_refresh(db, item)
    item = db.scalar(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.id == item.id)
    )
    return serialize_shopping_item(item)

@router.delete("/shopping-list/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, ShoppingListItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
