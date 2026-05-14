# Сервис планирования питания и рецептов

MVP веб-приложения на FastAPI + Vue.js + PostgreSQL. В проекте есть роли `admin` и `user`: админ наполняет каталоги, пользователь ведет продукты дома, планирует питание и формирует список покупок.

## Быстрый старт

1. Запустить PostgreSQL:

```bash
docker compose up -d postgres
```

2. Подготовить backend:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
cp .env.example .env
DATABASE_URL=postgresql+psycopg://meal:meal@127.0.0.1:5432/meal_planner ../.venv/bin/alembic upgrade head
DATABASE_URL=postgresql+psycopg://meal:meal@127.0.0.1:5432/meal_planner ../.venv/bin/python -m app.seed
../.venv/bin/uvicorn app.main:app --reload
```

3. Запустить frontend:

```bash
cd frontend
npm install
npm run dev
```

4. Открыть приложение:

```text
http://localhost:5173
```

Стартовый администратор после seed:

```text
admin@example.com / admin123
```

## Проверки

Backend:

```bash
cd backend
../.venv/bin/python -m pytest -q
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Что входит в MVP

- Регистрация, вход, выход, профиль текущего пользователя.
- Роли `admin` и `user`.
- Admin CRUD для категорий, ингредиентов, магазинов, цен, рецептов и ролей пользователей.
- Категории продуктов: овощи, фрукты, мясо, рыба и морепродукты, молочные продукты, яйца, крупы и макароны, бобовые, специи и соусы, напитки, хлеб и выпечка, замороженные продукты, консервы, сладости и снеки, прочее.
- Единый список продуктов дома с цветовой индикацией срока годности.
- Подбор рецептов с расчетом недостающих ингредиентов и ориентировочной стоимости.
- Месячный календарь питания, редактор дня по клику, слоты завтрак/обед/ужин.
- Автогенерация недельного плана.
- Список покупок из плана с группировкой по категориям и ручными позициями.
