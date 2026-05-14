"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("preferences", sa.Text(), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("diet", sa.String(length=120), nullable=True),
        sa.Column("favorite_dishes", sa.Text(), nullable=True),
        sa.Column("weekly_budget", sa.Float(), nullable=True),
        sa.Column("monthly_budget", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("unit", sa.String(length=12), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
    )
    op.create_index("ix_ingredients_name", "ingredients", ["name"], unique=True)

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("steps", sa.Text(), nullable=False),
        sa.Column("cooking_time", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("meal_type", sa.String(length=24), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
    )
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=False)

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
        sa.Column("store_id", sa.Integer(), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("price_per_unit", sa.Float(), nullable=False),
        sa.UniqueConstraint("ingredient_id", "store_id"),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=True),
    )

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.UniqueConstraint("recipe_id", "ingredient_id"),
    )

    op.create_table(
        "meal_plan_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("planned_date", sa.Date(), nullable=False),
        sa.Column("meal_slot", sa.String(length=24), nullable=False),
        sa.UniqueConstraint("user_id", "planned_date", "meal_slot"),
    )
    op.create_index("ix_meal_plan_entries_planned_date", "meal_plan_entries", ["planned_date"])

    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=12), nullable=False),
        sa.Column("is_purchased", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=24), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("shopping_list_items")
    op.drop_index("ix_meal_plan_entries_planned_date", table_name="meal_plan_entries")
    op.drop_table("meal_plan_entries")
    op.drop_table("recipe_ingredients")
    op.drop_table("inventory_items")
    op.drop_table("prices")
    op.drop_index("ix_recipes_title", table_name="recipes")
    op.drop_table("recipes")
    op.drop_index("ix_ingredients_name", table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_table("stores")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
