# Backend Modularization Design

## Goal

Refactor the backend into clear domain modules while preserving current application behavior, public API routes, and database semantics.

The current MVP backend works, but several unrelated responsibilities are concentrated in a few large files:

- `app/api.py` contains authentication, admin CRUD, catalog, inventory, recipes, planner, and shopping-list routes.
- `app/services.py` contains business logic for multiple unrelated domains.
- `app/models.py` and `app/schemas.py` already group several separate concepts in one place.

The refactor should make the codebase easier to navigate, safer to change, and easier to extend without introducing unnecessary architecture for the current product stage.

## Chosen Approach

Use a **domain-oriented modular structure**.

This is intentionally more structured than simply splitting one large router file into several files, but less elaborate than introducing repositories, use-case classes, or a fully layered architecture. It gives the project meaningful boundaries now without overbuilding for an MVP.

## Target Structure

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
      router.py
      schemas.py
    admin/
      router.py
    catalog/
      router.py
      schemas.py
    recipes/
      router.py
      schemas.py
      service.py
    inventory/
      router.py
      schemas.py
      service.py
    planner/
      router.py
      schemas.py
      service.py
    shopping/
      router.py
      schemas.py
      service.py

  shared/
    crud.py
    serializers.py
```

## Module Responsibilities

### `auth`

Owns:

- registration
- login/logout
- current-user endpoint

Keeps using shared authentication helpers from `security.py`.

### `admin`

Owns admin-only CRUD endpoints for:

- users and roles
- categories
- ingredients
- stores
- prices
- recipes

This module is primarily an HTTP orchestration layer over shared models and existing domain services.

### `catalog`

Owns user-facing reference data:

- active categories
- ingredients
- stores

### `inventory`

Owns:

- household inventory CRUD
- expiration status calculation
- inventory-specific serialization

### `recipes`

Owns:

- recipe listing and filtering
- ingredient availability analysis
- estimated missing-cost calculation
- recipe loading helpers

### `planner`

Owns:

- weekly plan generation
- monthly plan retrieval
- day retrieval and replacement
- recipe selection rules for generated plans

### `shopping`

Owns:

- generated shopping items from planned meals
- manual shopping items
- purchased-state toggling
- shopping-list serialization

## Shared Infrastructure

The following remain application-wide infrastructure rather than domain modules:

- `config.py`
- `database.py`
- `security.py`

The `shared/` package should remain intentionally small:

- `crud.py` for generic helpers such as `get_or_404` and `commit_refresh`
- `serializers.py` only for serialization helpers genuinely reused across multiple modules, such as category or ingredient serialization

Shared code must not become a second generic dumping ground.

## Dependency Direction

Preferred flow:

```text
router -> service -> models/database
```

Rules:

- Routers handle HTTP concerns: request parsing, dependencies, response models, and status codes.
- Services contain business rules and orchestration that are not purely HTTP-specific.
- Models contain ORM entities only.
- Schemas contain Pydantic request/response contracts only.
- Domain modules may use shared infrastructure.
- Domain modules should avoid importing each other's routers.
- Cross-domain reuse should happen through narrow service helpers or shared utilities, not through circular imports.

## Compatibility Constraints

The refactor must preserve:

- existing API paths
- request and response shapes
- authorization behavior
- database schema and Alembic migrations
- current frontend compatibility

This is a structural refactor, not a product-behavior change.

## Migration Strategy

The refactor should be performed incrementally:

1. Introduce package structure and shared helpers.
2. Split schemas into domain files while keeping equivalent field definitions.
3. Split ORM models into domain files and re-export them through `models/__init__.py`.
4. Move service logic into domain services.
5. Move route groups into domain routers.
6. Update `main.py` to include all routers.
7. Keep or add regression tests so existing behavior remains unchanged.

At each stage, imports should be updated before moving to the next stage, and the backend test suite should remain green.

## Testing Strategy

The current end-to-end MVP tests in `backend/tests/test_mvp.py` are the main regression safety net and should keep passing unchanged.

During the refactor:

- preserve route-level coverage for auth, admin CRUD, inventory, recipes, planner, and shopping list flows
- add focused tests only where moving logic reveals a missing seam or a non-obvious behavior that is currently unprotected
- prefer regression protection over expanding scope

## Out of Scope

This refactor does **not** include:

- changing API semantics
- changing database tables or migrations
- adding a repository layer
- introducing CQRS/use-case classes
- redesigning authentication
- touching the frontend except where a future backend change explicitly requires it

## Expected Outcome

After the refactor:

- each backend area has a clear home
- new work can be localized to fewer files
- large all-purpose files disappear
- the project is easier to reason about without becoming overengineered
