from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Category, Ingredient, Price, Recipe, RecipeIngredient, Store, User
from app.modules.auth.schemas import UserRead, UserRoleUpdate
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
from app.modules.recipes.schemas import RecipeCreate, RecipeRead
from app.modules.recipes.service import load_recipes_query
from app.security import require_admin
from app.shared.crud import commit_refresh, get_or_404


router = APIRouter()
@router.get("/admin/users", response_model=list[UserRead])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id.asc())).all()

@router.patch("/admin/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_or_404(db, User, user_id)
    user.role = payload.role
    return commit_refresh(db, user)

@router.get("/admin/categories", response_model=list[CategoryRead])
def list_categories(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name.asc())).all()

@router.post(
    "/admin/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
def create_category(
    payload: CategoryCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    category = Category(name=payload.name.strip(), is_active=payload.is_active)
    return commit_refresh(db, category)

@router.put("/admin/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    category = get_or_404(db, Category, category_id)
    category.name = payload.name.strip()
    category.is_active = payload.is_active
    return commit_refresh(db, category)

@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    category = get_or_404(db, Category, category_id)
    category.is_active = False
    db.commit()

@router.get("/admin/ingredients", response_model=list[IngredientRead])
def list_ingredients(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(
        select(Ingredient)
        .options(joinedload(Ingredient.category))
        .order_by(Ingredient.name.asc())
    ).all()

@router.post(
    "/admin/ingredients", response_model=IngredientRead, status_code=status.HTTP_201_CREATED
)
def create_ingredient(
    payload: IngredientCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    get_or_404(db, Category, payload.category_id)
    ingredient = Ingredient(
        name=payload.name.strip(), unit=payload.unit, category_id=payload.category_id
    )
    return commit_refresh(db, ingredient)

@router.put("/admin/ingredients/{ingredient_id}", response_model=IngredientRead)
def update_ingredient(
    ingredient_id: int,
    payload: IngredientCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ingredient = get_or_404(db, Ingredient, ingredient_id)
    get_or_404(db, Category, payload.category_id)
    ingredient.name = payload.name.strip()
    ingredient.unit = payload.unit
    ingredient.category_id = payload.category_id
    return commit_refresh(db, ingredient)

@router.delete("/admin/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    ingredient = get_or_404(db, Ingredient, ingredient_id)
    db.delete(ingredient)
    db.commit()

@router.get("/admin/stores", response_model=list[StoreRead])
def list_stores(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Store).order_by(Store.name.asc())).all()

@router.post("/admin/stores", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    store = Store(name=payload.name.strip(), is_active=payload.is_active)
    return commit_refresh(db, store)

@router.put("/admin/stores/{store_id}", response_model=StoreRead)
def update_store(
    store_id: int,
    payload: StoreCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    store = get_or_404(db, Store, store_id)
    store.name = payload.name.strip()
    store.is_active = payload.is_active
    return commit_refresh(db, store)

@router.delete("/admin/stores/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(store_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    store = get_or_404(db, Store, store_id)
    store.is_active = False
    db.commit()

@router.get("/admin/prices", response_model=list[PriceRead])
def list_prices(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(
        select(Price)
        .options(
            joinedload(Price.ingredient).joinedload(Ingredient.category),
            joinedload(Price.store),
        )
        .order_by(Price.id.asc())
    ).all()

@router.post("/admin/prices", response_model=PriceRead, status_code=status.HTTP_201_CREATED)
def create_price(
    payload: PriceCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    get_or_404(db, Ingredient, payload.ingredient_id)
    get_or_404(db, Store, payload.store_id)
    existing = db.scalar(
        select(Price).where(
            Price.ingredient_id == payload.ingredient_id,
            Price.store_id == payload.store_id,
        )
    )
    if existing:
        existing.price_per_unit = payload.price_per_unit
        return commit_refresh(db, existing)
    price = Price(
        ingredient_id=payload.ingredient_id,
        store_id=payload.store_id,
        price_per_unit=payload.price_per_unit,
    )
    return commit_refresh(db, price)

@router.put("/admin/prices/{price_id}", response_model=PriceRead)
def update_price(
    price_id: int,
    payload: PriceCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    price = get_or_404(db, Price, price_id)
    get_or_404(db, Ingredient, payload.ingredient_id)
    get_or_404(db, Store, payload.store_id)
    price.ingredient_id = payload.ingredient_id
    price.store_id = payload.store_id
    price.price_per_unit = payload.price_per_unit
    return commit_refresh(db, price)

@router.delete("/admin/prices/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price(price_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    price = get_or_404(db, Price, price_id)
    db.delete(price)
    db.commit()

@router.get("/admin/recipes", response_model=list[RecipeRead])
def admin_list_recipes(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(load_recipes_query().order_by(Recipe.title.asc())).unique().all()

@router.post("/admin/recipes", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    payload: RecipeCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    recipe = Recipe(
        title=payload.title.strip(),
        description=payload.description,
        steps=payload.steps,
        cooking_time=payload.cooking_time,
        difficulty=payload.difficulty,
        calories=payload.calories,
        meal_type=payload.meal_type,
        image_url=str(payload.image_url) if payload.image_url else None,
    )
    for item in payload.ingredients:
        get_or_404(db, Ingredient, item.ingredient_id)
        recipe.ingredients.append(
            RecipeIngredient(ingredient_id=item.ingredient_id, quantity=item.quantity)
        )
    return commit_refresh(db, recipe)

@router.put("/admin/recipes/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: int,
    payload: RecipeCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    recipe = get_or_404(db, Recipe, recipe_id)
    recipe.title = payload.title.strip()
    recipe.description = payload.description
    recipe.steps = payload.steps
    recipe.cooking_time = payload.cooking_time
    recipe.difficulty = payload.difficulty
    recipe.calories = payload.calories
    recipe.meal_type = payload.meal_type
    recipe.image_url = str(payload.image_url) if payload.image_url else None
    recipe.ingredients.clear()
    for item in payload.ingredients:
        get_or_404(db, Ingredient, item.ingredient_id)
        recipe.ingredients.append(
            RecipeIngredient(ingredient_id=item.ingredient_id, quantity=item.quantity)
        )
    return commit_refresh(db, recipe)

@router.delete("/admin/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    recipe = get_or_404(db, Recipe, recipe_id)
    db.delete(recipe)
    db.commit()
