from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    Category,
    Ingredient,
    InventoryItem,
    MealPlanEntry,
    Price,
    Recipe,
    RecipeIngredient,
    ShoppingListItem,
    Store,
    User,
)
from app.schemas import (
    CategoryCreate,
    CategoryRead,
    DayResponse,
    DayUpdateRequest,
    GenerateWeekRequest,
    IngredientCreate,
    IngredientRead,
    InventoryCreate,
    InventoryRead,
    LoginRequest,
    PlannerResponse,
    PriceCreate,
    PriceRead,
    RecipeCreate,
    RecipeRead,
    ShoppingGenerateRequest,
    ShoppingItemCreate,
    ShoppingItemPatch,
    ShoppingItemRead,
    ShoppingListResponse,
    StoreCreate,
    StoreRead,
    UserCreate,
    UserRead,
    UserRoleUpdate,
)
from app.security import (
    clear_auth_cookie,
    get_current_user,
    hash_password,
    require_admin,
    set_auth_cookie,
    verify_password,
)
from app.services import (
    expiration_status,
    generate_shopping_items,
    generate_week_plan,
    load_recipes_query,
    planned_entries,
    recipe_analysis,
    serialize_shopping_item,
)


router = APIRouter()


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


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        role="user",
        preferences=payload.preferences,
        allergies=payload.allergies,
        diet=payload.diet,
        favorite_dishes=payload.favorite_dishes,
        weekly_budget=payload.weekly_budget,
        monthly_budget=payload.monthly_budget,
    )
    commit_refresh(db, user)
    set_auth_cookie(response, user)
    return user


@router.post("/auth/login", response_model=UserRead)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    set_auth_cookie(response, user)
    return user


@router.post("/auth/logout")
def logout(response: Response):
    clear_auth_cookie(response)
    return {"ok": True}


@router.get("/auth/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user


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


@router.get("/catalog/categories", response_model=list[CategoryRead])
def catalog_categories(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.scalars(
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.name.asc())
    ).all()


@router.get("/catalog/ingredients", response_model=list[IngredientRead])
def catalog_ingredients(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.scalars(
        select(Ingredient)
        .options(joinedload(Ingredient.category))
        .join(Ingredient.category)
        .where(Category.is_active.is_(True))
        .order_by(Ingredient.name.asc())
    ).all()


@router.get("/catalog/stores", response_model=list[StoreRead])
def catalog_stores(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Store).where(Store.is_active.is_(True)).order_by(Store.name.asc())
    ).all()


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


@router.get("/recipes", response_model=list[RecipeRead])
def list_recipes(
    q: str | None = None,
    meal_type: str | None = None,
    difficulty: str | None = None,
    max_time: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = load_recipes_query().order_by(Recipe.title.asc())
    if q:
        query = query.where(Recipe.title.ilike(f"%{q}%"))
    if meal_type:
        query = query.where(Recipe.meal_type == meal_type)
    if difficulty:
        query = query.where(Recipe.difficulty == difficulty)
    if max_time:
        query = query.where(Recipe.cooking_time <= max_time)
    recipes = db.scalars(query).unique().all()
    return [recipe_analysis(db, recipe, user) for recipe in recipes]


@router.post("/planner/generate-week", response_model=PlannerResponse)
def generate_week(
    payload: GenerateWeekRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    generate_week_plan(db, user, payload.start_date)
    return {"entries": planned_entries(db, user, payload.start_date, 7)}


@router.get("/planner/month/{year}/{month}", response_model=PlannerResponse)
def get_month_plan(
    year: int,
    month: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start = date(year, month, 1)
    if month == 12:
        days = (date(year + 1, 1, 1) - start).days
    else:
        days = (date(year, month + 1, 1) - start).days
    return {"entries": planned_entries(db, user, start, days)}


@router.get("/planner/day/{planned_date}", response_model=DayResponse)
def get_day(
    planned_date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"date": planned_date, "entries": planned_entries(db, user, planned_date, 1)}


@router.put("/planner/day/{planned_date}", response_model=DayResponse)
def update_day(
    planned_date: date,
    payload: DayUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.scalars(
        select(MealPlanEntry).where(
            MealPlanEntry.user_id == user.id, MealPlanEntry.planned_date == planned_date
        )
    ).all()
    for entry in existing:
        db.delete(entry)
    db.flush()
    for entry in payload.entries:
        get_or_404(db, Recipe, entry.recipe_id)
        db.add(
            MealPlanEntry(
                user_id=user.id,
                recipe_id=entry.recipe_id,
                planned_date=planned_date,
                meal_slot=entry.meal_slot,
            )
        )
    db.commit()
    return {"date": planned_date, "entries": planned_entries(db, user, planned_date, 1)}


@router.get("/shopping-list", response_model=ShoppingListResponse)
def list_shopping_items(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    items = db.scalars(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.user_id == user.id)
        .order_by(ShoppingListItem.source.asc(), ShoppingListItem.title.asc())
    ).all()
    return {"items": [serialize_shopping_item(item) for item in items]}


@router.post("/shopping-list/generate", response_model=ShoppingListResponse)
def generate_shopping_list(
    payload: ShoppingGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    generate_shopping_items(db, user, payload.start_date, payload.days)
    return list_shopping_items(user, db)


@router.post(
    "/shopping-list", response_model=ShoppingItemRead, status_code=status.HTTP_201_CREATED
)
def create_shopping_item(
    payload: ShoppingItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ingredient = db.get(Ingredient, payload.ingredient_id) if payload.ingredient_id else None
    item = ShoppingListItem(
        user_id=user.id,
        ingredient_id=ingredient.id if ingredient else None,
        title=payload.title.strip(),
        quantity=payload.quantity,
        unit=payload.unit,
        source="manual",
    )
    commit_refresh(db, item)
    item = db.scalar(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.id == item.id)
    )
    return serialize_shopping_item(item)


@router.patch("/shopping-list/{item_id}", response_model=ShoppingItemRead)
def patch_shopping_item(
    item_id: int,
    payload: ShoppingItemPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, ShoppingListItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    item.is_purchased = payload.is_purchased
    commit_refresh(db, item)
    item = db.scalar(
        select(ShoppingListItem)
        .options(joinedload(ShoppingListItem.ingredient).joinedload(Ingredient.category))
        .where(ShoppingListItem.id == item.id)
    )
    return serialize_shopping_item(item)


@router.delete("/shopping-list/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_or_404(db, ShoppingListItem, item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
