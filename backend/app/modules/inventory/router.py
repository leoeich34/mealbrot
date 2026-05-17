from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Ingredient, InventoryItem, User
from app.modules.inventory.schemas import InventoryCreate, InventoryRead
from app.modules.inventory.service import expiration_status
from app.security import get_current_user
from app.shared.crud import commit_refresh, get_or_404


router = APIRouter()
@router.get("/inventory", response_model=list[InventoryRead])
def list_inventory(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(InventoryItem)
        .options(joinedload(InventoryItem.ingredient).joinedload(Ingredient.category))
        .where(InventoryItem.user_id == user.id)
        .order_by(InventoryItem.id.asc())
    ).all()
    return [
        {
            "id": item.id,
            "ingredient": item.ingredient,
            "quantity": item.quantity,
            "expiration_date": item.expiration_date,
            "expiration_status": expiration_status(item.expiration_date),
        }
        for item in items
    ]

@router.post("/inventory", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_or_404(db, Ingredient, payload.ingredient_id)
    item = InventoryItem(
        user_id=user.id,
        ingredient_id=payload.ingredient_id,
        quantity=payload.quantity,
        expiration_date=payload.expiration_date,
    )
    commit_refresh(db, item)
    item = db.scalar(
        select(InventoryItem)
        .options(joinedload(InventoryItem.ingredient).joinedload(Ingredient.category))
        .where(InventoryItem.id == item.id)
    )
    return {
        "id": item.id,
        "ingredient": item.ingredient,
        "quantity": item.quantity,
        "expiration_date": item.expiration_date,
        "expiration_status": expiration_status(item.expiration_date),
    }

@router.put("/inventory/{item_id}", response_model=InventoryRead)
def update_inventory_item(
    item_id: int,
    payload: InventoryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, InventoryItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    get_or_404(db, Ingredient, payload.ingredient_id)
    item.ingredient_id = payload.ingredient_id
    item.quantity = payload.quantity
    item.expiration_date = payload.expiration_date
    commit_refresh(db, item)
    item = db.scalar(
        select(InventoryItem)
        .options(joinedload(InventoryItem.ingredient).joinedload(Ingredient.category))
        .where(InventoryItem.id == item.id)
    )
    return {
        "id": item.id,
        "ingredient": item.ingredient,
        "quantity": item.quantity,
        "expiration_date": item.expiration_date,
        "expiration_status": expiration_status(item.expiration_date),
    }

@router.delete("/inventory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, InventoryItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
