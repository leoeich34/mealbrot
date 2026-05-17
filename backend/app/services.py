from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category
from app.shared.serializers import serialize_category, serialize_ingredient


def category_exists(db: Session, name: str) -> bool:
    return (
        db.scalar(select(func.count()).select_from(Category).where(Category.name == name))
        or 0
    ) > 0
