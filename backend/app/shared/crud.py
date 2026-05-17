from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, object_id: int):
    item = db.get(model, object_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item


def commit_refresh(db: Session, item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
