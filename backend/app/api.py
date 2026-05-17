"""Compatibility facade for domain router imports during modularization."""

from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.inventory.router import router as inventory_router
from app.modules.planner.router import router as planner_router
from app.modules.recipes.router import router as recipes_router
from app.modules.shopping.router import router as shopping_router

__all__ = [
    "admin_router",
    "auth_router",
    "catalog_router",
    "inventory_router",
    "planner_router",
    "recipes_router",
    "shopping_router",
]
