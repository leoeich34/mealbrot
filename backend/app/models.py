from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    diet: Mapped[str | None] = mapped_column(String(120), nullable=True)
    favorite_dishes: Mapped[str | None] = mapped_column(Text, nullable=True)
    weekly_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    meal_plan_entries: Mapped[list["MealPlanEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    shopping_items: Mapped[list["ShoppingListItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="category")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(12))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped[Category] = relationship(back_populates="ingredients")
    prices: Mapped[list["Price"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    prices: Mapped[list["Price"]] = relationship(
        back_populates="store", cascade="all, delete-orphan"
    )


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint("ingredient_id", "store_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    price_per_unit: Mapped[float] = mapped_column(Float)

    ingredient: Mapped[Ingredient] = relationship(back_populates="prices")
    store: Mapped[Store] = relationship(back_populates="prices")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(40), default="easy")
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_type: Mapped[str] = mapped_column(String(24), default="dinner")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float] = mapped_column(Float)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship()


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float] = mapped_column(Float)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped[User] = relationship(back_populates="inventory_items")
    ingredient: Mapped[Ingredient] = relationship()


class MealPlanEntry(Base):
    __tablename__ = "meal_plan_entries"
    __table_args__ = (UniqueConstraint("user_id", "planned_date", "meal_slot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    planned_date: Mapped[date] = mapped_column(Date, index=True)
    meal_slot: Mapped[str] = mapped_column(String(24))

    user: Mapped[User] = relationship(back_populates="meal_plan_entries")
    recipe: Mapped[Recipe] = relationship()


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(180))
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(12))
    is_purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(24), default="manual")

    user: Mapped[User] = relationship(back_populates="shopping_items")
    ingredient: Mapped[Ingredient | None] = relationship()
