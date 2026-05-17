# Backend Modularization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the backend into domain-oriented modules while preserving existing routes, behavior, database schema, and frontend compatibility.

**Architecture:** Keep FastAPI, SQLAlchemy, and the current persistence model intact, but split the monolithic backend files into focused packages. Routers own HTTP concerns, services own business logic, schemas own Pydantic contracts, models are grouped by domain, and small shared helpers are extracted only where they are already reused.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Pytest.

---

## Target File Map

```text
backend/app/
  main.py
  config.py
  database.py
  security.py

  models/
    __init__.py
    users.py
    catalog.py
    recipes.py
    inventory.py
    planner.py
    shopping.py

  modules/
    auth/
      __init__.py
      router.py
      schemas.py
    admin/
      __init__.py
      router.py
    catalog/
      __init__.py
      router.py
      schemas.py
    recipes/
      __init__.py
      router.py
      schemas.py
      service.py
    inventory/
      __init__.py
      router.py
      schemas.py
      service.py
    planner/
      __init__.py
      router.py
      schemas.py
      service.py
    shopping/
      __init__.py
      router.py
      schemas.py
      service.py

  shared/
    __init__.py
    crud.py
    serializers.py
```

## Task 1: Protect the refactor with route regression checks

**Files:**
- Modify: `backend/tests/test_mvp.py`

- [ ] **Step 1: Add a smoke test for route availability**

```python
def test_app_registers_expected_routes():
    routes = {route.path for route in app.routes}

    assert {
        "/auth/register",
        "/auth/login",
        "/auth/logout",
        "/auth/me",
        "/admin/users",
        "/admin/categories",
        "/admin/ingredients",
        "/admin/stores",
        "/admin/prices",
        "/admin/recipes",
        "/catalog/categories",
        "/catalog/ingredients",
        "/catalog/stores",
        "/inventory",
        "/recipes",
        "/planner/generate-week",
        "/planner/month/{year}/{month}",
        "/planner/day/{planned_date}",
        "/shopping-list",
        "/shopping-list/generate",
    }.issubset(routes)
```

- [ ] **Step 2: Run the focused test and confirm it passes before restructuring**

Run: `python -m pytest backend/tests/test_mvp.py::test_app_registers_expected_routes -q`

Expected: `1 passed`

- [ ] **Step 3: Commit the regression guard**

```bash
git add backend/tests/test_mvp.py
git commit -m "test: protect backend route surface before modularization"
```

## Task 2: Create shared helpers and split Pydantic schemas by domain

**Files:**
- Create: `backend/app/shared/__init__.py`
- Create: `backend/app/shared/crud.py`
- Create: `backend/app/shared/serializers.py`
- Create: `backend/app/modules/auth/__init__.py`
- Create: `backend/app/modules/auth/schemas.py`
- Create: `backend/app/modules/catalog/__init__.py`
- Create: `backend/app/modules/catalog/schemas.py`
- Create: `backend/app/modules/recipes/__init__.py`
- Create: `backend/app/modules/recipes/schemas.py`
- Create: `backend/app/modules/inventory/__init__.py`
- Create: `backend/app/modules/inventory/schemas.py`
- Create: `backend/app/modules/planner/__init__.py`
- Create: `backend/app/modules/planner/schemas.py`
- Create: `backend/app/modules/shopping/__init__.py`
- Create: `backend/app/modules/shopping/schemas.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/api.py`

- [ ] **Step 1: Move generic CRUD helpers into `shared/crud.py`**

```python
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
```

- [ ] **Step 2: Move reused serializers into `shared/serializers.py`**

```python
from app.models import Ingredient


def serialize_category(category):
    return {"id": category.id, "name": category.name, "is_active": category.is_active}


def serialize_ingredient(ingredient: Ingredient) -> dict:
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "unit": ingredient.unit,
        "category": serialize_category(ingredient.category),
    }
```

- [ ] **Step 3: Move auth schemas**

`backend/app/modules/auth/schemas.py`

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]
```

- [ ] **Step 4: Move catalog schemas**

`backend/app/modules/catalog/schemas.py`

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Unit = Literal["g", "ml", "pcs"]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    is_active: bool = True


class CategoryRead(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    unit: Unit
    category_id: int


class IngredientRead(BaseModel):
    id: int
    name: str
    unit: Unit
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)


class StoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    is_active: bool = True


class StoreRead(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PriceCreate(BaseModel):
    ingredient_id: int
    store_id: int
    price_per_unit: float = Field(gt=0)


class PriceRead(BaseModel):
    id: int
    ingredient: IngredientRead
    store: StoreRead
    price_per_unit: float

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 5: Move recipe, inventory, planner, and shopping schemas**

Create domain schema files by moving these existing definitions unchanged from `backend/app/schemas.py`:

- `modules/recipes/schemas.py`: `MealSlot`, `RecipeIngredientCreate`, `RecipeCreate`, `RecipeIngredientRead`, `MissingIngredientRead`, `RecipeRead`
- `modules/inventory/schemas.py`: `InventoryCreate`, `InventoryRead`
- `modules/planner/schemas.py`: `GenerateWeekRequest`, `DayEntryCreate`, `DayUpdateRequest`, `MealPlanEntryRead`, `PlannerResponse`, `DayResponse`
- `modules/shopping/schemas.py`: `ShoppingGenerateRequest`, `ShoppingItemCreate`, `ShoppingItemPatch`, `ShoppingItemRead`, `ShoppingListResponse`

Keep the field definitions exactly equivalent to the current `schemas.py`.

- [ ] **Step 6: Turn `app/schemas.py` into a compatibility facade**

```python
from app.modules.auth.schemas import LoginRequest, UserCreate, UserRead, UserRoleUpdate
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    IngredientCreate,
    IngredientRead,
    PriceCreate,
    PriceRead,
    StoreCreate,
    StoreRead,
)
from app.modules.inventory.schemas import InventoryCreate, InventoryRead
from app.modules.planner.schemas import (
    DayResponse,
    DayUpdateRequest,
    GenerateWeekRequest,
    PlannerResponse,
)
from app.modules.recipes.schemas import RecipeCreate, RecipeRead
from app.modules.shopping.schemas import (
    ShoppingGenerateRequest,
    ShoppingItemCreate,
    ShoppingItemPatch,
    ShoppingItemRead,
    ShoppingListResponse,
)
```

- [ ] **Step 7: Update `app/api.py` imports to use shared helpers**

Replace local `get_or_404` and `commit_refresh` definitions with:

```python
from app.shared.crud import commit_refresh, get_or_404
```

- [ ] **Step 8: Run backend tests**

Run: `python -m pytest backend/tests/test_mvp.py -q`

Expected: all tests pass.

- [ ] **Step 9: Commit the schema split**

```bash
git add backend/app backend/tests/test_mvp.py
git commit -m "refactor: split backend schemas into domain modules"
```

## Task 3: Split ORM models into domain files

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/users.py`
- Create: `backend/app/models/catalog.py`
- Create: `backend/app/models/recipes.py`
- Create: `backend/app/models/inventory.py`
- Create: `backend/app/models/planner.py`
- Create: `backend/app/models/shopping.py`
- Delete: `backend/app/models.py`
- Modify: `backend/alembic/env.py`
- Modify: `backend/app/seed.py`
- Modify: backend imports that reference `app.models`

- [ ] **Step 1: Move `User` into `models/users.py`**

Include only the `User` model and its relationships.

- [ ] **Step 2: Move `Category`, `Ingredient`, `Store`, and `Price` into `models/catalog.py`**

Preserve all table names, constraints, relationships, and defaults unchanged.

- [ ] **Step 3: Move `Recipe` and `RecipeIngredient` into `models/recipes.py`**

Preserve the existing `Recipe.ingredients` relationship and recipe-ingredient uniqueness constraint.

- [ ] **Step 4: Move `InventoryItem` into `models/inventory.py`**

- [ ] **Step 5: Move `MealPlanEntry` into `models/planner.py`**

- [ ] **Step 6: Move `ShoppingListItem` into `models/shopping.py`**

- [ ] **Step 7: Re-export all ORM models from `models/__init__.py`**

```python
from app.models.catalog import Category, Ingredient, Price, Store
from app.models.inventory import InventoryItem
from app.models.planner import MealPlanEntry
from app.models.recipes import Recipe, RecipeIngredient
from app.models.shopping import ShoppingListItem
from app.models.users import User

__all__ = [
    "Category",
    "Ingredient",
    "InventoryItem",
    "MealPlanEntry",
    "Price",
    "Recipe",
    "RecipeIngredient",
    "ShoppingListItem",
    "Store",
    "User",
]
```

- [ ] **Step 8: Update imports without changing call sites**

Keep consumers importing from `app.models`, but make that path resolve through the new package.

- [ ] **Step 9: Verify Alembic model discovery still works**

Run: `python -m pytest backend/tests/test_mvp.py -q`

Expected: all tests pass and metadata creation succeeds.

- [ ] **Step 10: Commit the model split**

```bash
git add backend/app backend/alembic
git commit -m "refactor: split backend models by domain"
```

## Task 4: Move business logic into domain services

**Files:**
- Create: `backend/app/modules/recipes/service.py`
- Create: `backend/app/modules/inventory/service.py`
- Create: `backend/app/modules/planner/service.py`
- Create: `backend/app/modules/shopping/service.py`
- Modify: `backend/app/services.py`
- Modify: `backend/app/api.py`
- Modify: `backend/tests/test_mvp.py`

- [ ] **Step 1: Move inventory logic**

Move unchanged:

- `expiration_status`
- `inventory_totals`

into `modules/inventory/service.py`.

- [ ] **Step 2: Move recipe logic**

Move unchanged:

- `cheapest_price`
- `estimate_cost`
- `recipe_analysis`
- `load_recipes_query`
- `recipe_is_allowed_for_user`

into `modules/recipes/service.py`.

- [ ] **Step 3: Move planner logic**

Move unchanged:

- `MEAL_SLOTS`
- `choose_recipe_for_slot`
- `generate_week_plan`
- `planned_entries`

into `modules/planner/service.py`.

- [ ] **Step 4: Move shopping logic**

Move unchanged:

- `generate_shopping_items`
- `serialize_shopping_item`

into `modules/shopping/service.py`.

- [ ] **Step 5: Keep `category_exists` accessible**

Leave `category_exists` in `app/services.py` temporarily as the only remaining helper, or move it into a clearly justified shared/catalog location and update the single test import accordingly.

- [ ] **Step 6: Update imports in `app/api.py`**

Replace `from app.services import (...)` with imports from the new domain services.

- [ ] **Step 7: Run backend tests**

Run: `python -m pytest backend/tests/test_mvp.py -q`

Expected: all tests pass.

- [ ] **Step 8: Commit the service split**

```bash
git add backend/app backend/tests/test_mvp.py
git commit -m "refactor: split backend services by domain"
```

## Task 5: Split HTTP routes into domain routers

**Files:**
- Create: `backend/app/modules/auth/router.py`
- Create: `backend/app/modules/admin/router.py`
- Create: `backend/app/modules/catalog/router.py`
- Create: `backend/app/modules/recipes/router.py`
- Create: `backend/app/modules/inventory/router.py`
- Create: `backend/app/modules/planner/router.py`
- Create: `backend/app/modules/shopping/router.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api.py`

- [ ] **Step 1: Move auth endpoints into `modules/auth/router.py`**

Move unchanged:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

- [ ] **Step 2: Move admin endpoints into `modules/admin/router.py`**

Move unchanged:

- `/admin/users`
- `/admin/categories`
- `/admin/ingredients`
- `/admin/stores`
- `/admin/prices`
- `/admin/recipes`

- [ ] **Step 3: Move catalog endpoints into `modules/catalog/router.py`**

Move unchanged:

- `/catalog/categories`
- `/catalog/ingredients`
- `/catalog/stores`

- [ ] **Step 4: Move inventory endpoints into `modules/inventory/router.py`**

Move unchanged:

- `GET /inventory`
- `POST /inventory`
- `PUT /inventory/{item_id}`
- `DELETE /inventory/{item_id}`

- [ ] **Step 5: Move recipe endpoint into `modules/recipes/router.py`**

Move unchanged:

- `GET /recipes`

- [ ] **Step 6: Move planner endpoints into `modules/planner/router.py`**

Move unchanged:

- `POST /planner/generate-week`
- `GET /planner/month/{year}/{month}`
- `GET /planner/day/{planned_date}`
- `PUT /planner/day/{planned_date}`

- [ ] **Step 7: Move shopping endpoints into `modules/shopping/router.py`**

Move unchanged:

- `GET /shopping-list`
- `POST /shopping-list/generate`
- `POST /shopping-list`
- `PATCH /shopping-list/{item_id}`
- `DELETE /shopping-list/{item_id}`

- [ ] **Step 8: Include all routers from `main.py`**

```python
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.inventory.router import router as inventory_router
from app.modules.planner.router import router as planner_router
from app.modules.recipes.router import router as recipes_router
from app.modules.shopping.router import router as shopping_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(catalog_router)
app.include_router(inventory_router)
app.include_router(recipes_router)
app.include_router(planner_router)
app.include_router(shopping_router)
```

- [ ] **Step 9: Reduce `app/api.py` to a compatibility facade or remove it if no longer imported**

If retained for compatibility, use:

```python
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.inventory.router import router as inventory_router
from app.modules.planner.router import router as planner_router
from app.modules.recipes.router import router as recipes_router
from app.modules.shopping.router import router as shopping_router
```

and document that new code should import domain routers directly.

- [ ] **Step 10: Run route regression and full backend tests**

Run:

```bash
python -m pytest backend/tests/test_mvp.py::test_app_registers_expected_routes -q
python -m pytest backend/tests/test_mvp.py -q
```

Expected: all tests pass.

- [ ] **Step 11: Commit the router split**

```bash
git add backend/app backend/tests/test_mvp.py
git commit -m "refactor: split backend routers by domain"
```

## Task 6: Remove obsolete facades and verify repository health

**Files:**
- Modify or delete if no longer needed: `backend/app/api.py`
- Modify or delete if no longer needed: `backend/app/services.py`
- Modify or delete if no longer needed: `backend/app/schemas.py`
- Review: `backend/app/main.py`
- Review: `backend/tests/test_mvp.py`

- [ ] **Step 1: Identify whether compatibility facades are still needed**

Check for imports of:

- `app.api`
- `app.services`
- `app.schemas`

using:

```bash
python - <<'PY'
from pathlib import Path

for needle in ("app.api", "app.services", "app.schemas"):
    print(f"--- {needle} ---")
    for path in Path("backend").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if needle in text:
            print(path)
PY
```

- [ ] **Step 2: Remove only the facades that no code still imports**

Expected safe end state:

- `app/api.py` removed if `main.py` includes routers directly and no consumer imports it
- `app/services.py` removed or reduced to intentionally shared leftovers only
- `app/schemas.py` removed or retained only if there is a clear compatibility need

- [ ] **Step 3: Run the backend test suite**

Run: `python -m pytest backend/tests/test_mvp.py -q`

Expected: all tests pass.

- [ ] **Step 4: Run the repository-level backend test command from README**

Run from `backend/`:

```bash
python -m pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 5: Commit final cleanup**

```bash
git add backend/app backend/tests/test_mvp.py
git commit -m "refactor: finalize backend modular structure"
```

## Task 7: Final verification

**Files:**
- Review: `backend/app/`
- Review: `backend/tests/test_mvp.py`
- Review: `docs/superpowers/specs/2026-05-18-backend-modularization-design.md`

- [ ] **Step 1: Compare the final tree with the design spec**

Confirm the implementation matches:

- domain modules exist
- models are split by domain
- shared helpers stay minimal
- no public API route changed

- [ ] **Step 2: Run final backend verification**

Run:

```bash
cd backend
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Record any deliberate deviations from the original design**

If the implementation keeps a facade or merges a tiny module for pragmatic reasons, note it in the final summary instead of leaving the difference unexplained.
