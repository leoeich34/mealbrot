from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InventoryItem, User


def expiration_status(expiration_date: date | None, today: date | None = None) -> str:
    if expiration_date is None:
        return "unknown"
    current = today or date.today()
    if expiration_date < current:
        return "expired"
    if expiration_date <= current + timedelta(days=3):
        return "soon"
    return "fresh"


def inventory_totals(db: Session, user: User) -> dict[int, float]:
    totals: dict[int, float] = defaultdict(float)
    items = db.scalars(
        select(InventoryItem).where(InventoryItem.user_id == user.id)
    ).all()
    for item in items:
        if expiration_status(item.expiration_date) != "expired":
            totals[item.ingredient_id] += item.quantity
    return dict(totals)
