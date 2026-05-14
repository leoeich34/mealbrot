from sqlalchemy import select

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Category, User
from app.security import hash_password


DEFAULT_CATEGORIES = [
    "овощи",
    "фрукты",
    "мясо",
    "рыба и морепродукты",
    "молочные продукты",
    "яйца",
    "крупы и макароны",
    "бобовые",
    "специи и соусы",
    "напитки",
    "хлеб и выпечка",
    "замороженные продукты",
    "консервы",
    "сладости и снеки",
    "прочее",
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for name in DEFAULT_CATEGORIES:
            exists = db.scalar(select(Category).where(Category.name == name))
            if not exists:
                db.add(Category(name=name, is_active=True))

        admin = db.scalar(select(User).where(User.email == settings.seed_admin_email))
        if not admin:
            db.add(
                User(
                    name="Администратор",
                    email=settings.seed_admin_email,
                    password_hash=hash_password(settings.seed_admin_password),
                    role="admin",
                    weekly_budget=5000,
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
