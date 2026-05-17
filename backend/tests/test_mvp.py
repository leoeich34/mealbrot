from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.security import hash_password
from app.services import category_exists
from app.services import serialize_category as services_serialize_category
from app.services import serialize_ingredient as services_serialize_ingredient
from app.shared.serializers import serialize_category, serialize_ingredient
from app.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(
        User(
            name="Админ",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            weekly_budget=5000,
        )
    )
    db.commit()
    db.close()


def client():
    reset_database()
    return TestClient(app)


def login(api, email, password):
    response = api.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response


def test_app_registers_expected_routes():
    route_contracts = {
        (route.path, method)
        for route in app.routes
        for method in route.methods
        if method not in {"HEAD", "OPTIONS"}
    }

    assert route_contracts == {
        ("/openapi.json", "GET"),
        ("/docs", "GET"),
        ("/docs/oauth2-redirect", "GET"),
        ("/redoc", "GET"),
        ("/auth/register", "POST"),
        ("/auth/login", "POST"),
        ("/auth/logout", "POST"),
        ("/auth/me", "GET"),
        ("/admin/users", "GET"),
        ("/admin/users/{user_id}/role", "PATCH"),
        ("/admin/categories", "GET"),
        ("/admin/categories", "POST"),
        ("/admin/categories/{category_id}", "PUT"),
        ("/admin/categories/{category_id}", "DELETE"),
        ("/admin/ingredients", "GET"),
        ("/admin/ingredients", "POST"),
        ("/admin/ingredients/{ingredient_id}", "PUT"),
        ("/admin/ingredients/{ingredient_id}", "DELETE"),
        ("/admin/stores", "GET"),
        ("/admin/stores", "POST"),
        ("/admin/stores/{store_id}", "PUT"),
        ("/admin/stores/{store_id}", "DELETE"),
        ("/admin/prices", "GET"),
        ("/admin/prices", "POST"),
        ("/admin/prices/{price_id}", "PUT"),
        ("/admin/prices/{price_id}", "DELETE"),
        ("/admin/recipes", "GET"),
        ("/admin/recipes", "POST"),
        ("/admin/recipes/{recipe_id}", "PUT"),
        ("/admin/recipes/{recipe_id}", "DELETE"),
        ("/catalog/categories", "GET"),
        ("/catalog/ingredients", "GET"),
        ("/catalog/stores", "GET"),
        ("/inventory", "GET"),
        ("/inventory", "POST"),
        ("/inventory/{item_id}", "PUT"),
        ("/inventory/{item_id}", "DELETE"),
        ("/recipes", "GET"),
        ("/planner/generate-week", "POST"),
        ("/planner/month/{year}/{month}", "GET"),
        ("/planner/day/{planned_date}", "GET"),
        ("/planner/day/{planned_date}", "PUT"),
        ("/shopping-list", "GET"),
        ("/shopping-list", "POST"),
        ("/shopping-list/generate", "POST"),
        ("/shopping-list/{item_id}", "PATCH"),
        ("/shopping-list/{item_id}", "DELETE"),
        ("/health", "GET"),
    }


def create_user(api):
    response = api.post(
        "/auth/register",
        json={
            "name": "Леван",
            "email": "levan@example.com",
            "password": "secret123",
            "weekly_budget": 2500,
            "preferences": "простые блюда",
            "allergies": "арахис",
        },
    )
    assert response.status_code == 201
    return response


def admin_seed_catalog(api):
    login(api, "admin@example.com", "admin123")
    categories = {}
    for name in ["овощи", "мясо", "крупы и макароны", "молочные продукты"]:
        response = api.post("/admin/categories", json={"name": name})
        assert response.status_code == 201
        categories[name] = response.json()["id"]

    ingredients = {}
    for name, unit, category in [
        ("томаты", "g", "овощи"),
        ("курица", "g", "мясо"),
        ("рис", "g", "крупы и макароны"),
        ("молоко", "ml", "молочные продукты"),
    ]:
        response = api.post(
            "/admin/ingredients",
            json={"name": name, "unit": unit, "category_id": categories[category]},
        )
        assert response.status_code == 201
        ingredients[name] = response.json()["id"]

    store = api.post("/admin/stores", json={"name": "Домашний магазин"}).json()
    for name, price in [("томаты", 220), ("курица", 390), ("рис", 110), ("молоко", 95)]:
        response = api.post(
            "/admin/prices",
            json={
                "ingredient_id": ingredients[name],
                "store_id": store["id"],
                "price_per_unit": price,
            },
        )
        assert response.status_code == 201

    recipe = api.post(
        "/admin/recipes",
        json={
            "title": "Курица с рисом",
            "description": "Бюджетный ужин",
            "steps": "Сварить рис. Обжарить курицу с томатами.",
            "cooking_time": 35,
            "difficulty": "easy",
            "calories": 520,
            "meal_type": "dinner",
            "image_url": "https://example.com/chicken.jpg",
            "ingredients": [
                {"ingredient_id": ingredients["курица"], "quantity": 300},
                {"ingredient_id": ingredients["рис"], "quantity": 200},
                {"ingredient_id": ingredients["томаты"], "quantity": 150},
            ],
        },
    )
    assert recipe.status_code == 201
    return categories, ingredients, recipe.json()


def test_auth_register_login_and_user_cannot_access_admin_catalog():
    api = client()
    create_user(api)

    me = api.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "levan@example.com"
    assert me.json()["role"] == "user"

    denied = api.post("/admin/categories", json={"name": "овощи"})
    assert denied.status_code == 403

    api.post("/auth/logout")
    assert api.get("/auth/me").status_code == 401


def test_admin_catalog_crud_keeps_product_categories_required():
    api = client()
    login(api, "admin@example.com", "admin123")

    category = api.post("/admin/categories", json={"name": "овощи"}).json()
    ingredient = api.post(
        "/admin/ingredients",
        json={"name": "томаты", "unit": "g", "category_id": category["id"]},
    )
    assert ingredient.status_code == 201
    assert ingredient.json()["category"]["name"] == "овощи"

    missing_category = api.post(
        "/admin/ingredients", json={"name": "без категории", "unit": "g"}
    )
    assert missing_category.status_code == 422


def test_inventory_is_single_list_with_expiration_status_and_category():
    api = client()
    _, ingredients, _ = admin_seed_catalog(api)
    create_user(api)

    catalog = api.get("/catalog/ingredients")
    assert catalog.status_code == 200
    assert {item["name"] for item in catalog.json()} >= {"томаты", "курица", "рис"}

    today = date.today()
    for name, expiration in [
        ("томаты", today - timedelta(days=1)),
        ("курица", today + timedelta(days=1)),
        ("рис", today + timedelta(days=20)),
        ("молоко", None),
    ]:
        response = api.post(
            "/inventory",
            json={
                "ingredient_id": ingredients[name],
                "quantity": 500,
                "expiration_date": expiration.isoformat() if expiration else None,
            },
        )
        assert response.status_code == 201

    items = api.get("/inventory").json()
    assert [item["ingredient"]["name"] for item in items] == [
        "томаты",
        "курица",
        "рис",
        "молоко",
    ]
    assert [item["expiration_status"] for item in items] == [
        "expired",
        "soon",
        "fresh",
        "unknown",
    ]
    assert items[0]["ingredient"]["category"]["name"] == "овощи"


def test_recipes_show_missing_ingredients_and_estimated_cost():
    api = client()
    _, ingredients, _ = admin_seed_catalog(api)
    create_user(api)
    api.post(
        "/inventory",
        json={
            "ingredient_id": ingredients["рис"],
            "quantity": 200,
            "expiration_date": None,
        },
    )

    recipes = api.get("/recipes").json()
    recipe = recipes[0]
    assert recipe["title"] == "Курица с рисом"
    assert recipe["can_cook"] is False
    assert {item["ingredient"]["name"] for item in recipe["missing_ingredients"]} == {
        "курица",
        "томаты",
    }
    assert recipe["missing_cost"] > 0


def test_planner_generates_week_and_day_editor_updates_meals():
    api = client()
    _, ingredients, recipe = admin_seed_catalog(api)
    create_user(api)
    for name in ["курица", "рис", "томаты"]:
        api.post(
            "/inventory",
            json={
                "ingredient_id": ingredients[name],
                "quantity": 1000,
                "expiration_date": (date.today() + timedelta(days=2)).isoformat(),
            },
        )

    start = date.today().isoformat()
    generated = api.post("/planner/generate-week", json={"start_date": start})
    assert generated.status_code == 200
    assert len(generated.json()["entries"]) >= 1

    day = api.get(f"/planner/day/{start}").json()
    assert any(entry["recipe"]["id"] == recipe["id"] for entry in day["entries"])

    updated = api.put(
        f"/planner/day/{start}",
        json={"entries": [{"meal_slot": "breakfast", "recipe_id": recipe["id"]}]},
    )
    assert updated.status_code == 200
    assert updated.json()["entries"][0]["meal_slot"] == "breakfast"


def test_shopping_list_combines_missing_ingredients_by_category_and_manual_items():
    api = client()
    _, ingredients, recipe = admin_seed_catalog(api)
    create_user(api)
    start = date.today().isoformat()
    api.put(
        f"/planner/day/{start}",
        json={"entries": [{"meal_slot": "dinner", "recipe_id": recipe["id"]}]},
    )
    api.post(
        "/inventory",
        json={"ingredient_id": ingredients["рис"], "quantity": 50, "expiration_date": None},
    )

    generated = api.post("/shopping-list/generate", json={"start_date": start, "days": 1})
    assert generated.status_code == 200
    items = generated.json()["items"]
    names = {item["ingredient"]["name"]: item for item in items if item["ingredient"]}
    assert names["рис"]["quantity"] == 150
    assert names["курица"]["category"]["name"] == "мясо"

    manual = api.post(
        "/shopping-list",
        json={"title": "салфетки", "quantity": 1, "unit": "pcs"},
    )
    assert manual.status_code == 201
    checked = api.patch(f"/shopping-list/{manual.json()['id']}", json={"is_purchased": True})
    assert checked.status_code == 200
    assert checked.json()["is_purchased"] is True


def test_shopping_list_rejects_unknown_ingredient_ids():
    api = client()
    create_user(api)

    response = api.post(
        "/shopping-list",
        json={"title": "неизвестный товар", "quantity": 1, "unit": "pcs", "ingredient_id": 999},
    )

    assert response.status_code == 404


def test_category_exists_checks_category_names():
    api = client()
    login(api, "admin@example.com", "admin123")
    api.post("/admin/categories", json={"name": "овощи"})

    db = TestingSessionLocal()
    try:
        assert category_exists(db, "овощи") is True
        assert category_exists(db, "мясо") is False
    finally:
        db.close()


def test_services_use_shared_serializers():
    assert services_serialize_category is serialize_category
    assert services_serialize_ingredient is serialize_ingredient
