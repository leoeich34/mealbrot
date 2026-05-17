# Practical Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix confirmed application and CI/CD defects, then leave the repository with automated checks that block broken deploys.

**Architecture:** Keep the existing FastAPI and Vue structure intact. Add regression coverage around the faulty backend helper, introduce a dedicated CI workflow for backend/frontend validation, and make deploy depend on that CI workflow succeeding on `main`.

**Tech Stack:** FastAPI, SQLAlchemy, Pytest, Vue, Vitest, GitHub Actions, Docker Compose.

---

### Task 1: Confirm backend defect

**Files:**
- Modify: `backend/tests/test_mvp.py`
- Modify: `backend/app/services.py`

- [ ] **Step 1: Write the failing test**

```python
from app.services import category_exists


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
```

- [ ] **Step 2: Run the focused test and verify it fails because the helper queries the wrong table column**

Run: `python -m pytest backend/tests/test_mvp.py::test_category_exists_checks_category_names -q`

- [ ] **Step 3: Fix the helper minimally**

```python
def category_exists(db: Session, name: str) -> bool:
    return (
        db.scalar(select(func.count()).select_from(Category).where(Category.name == name))
        or 0
    ) > 0
```

- [ ] **Step 4: Re-run the focused test and confirm it passes**

Run: `python -m pytest backend/tests/test_mvp.py::test_category_exists_checks_category_names -q`

### Task 2: Add CI coverage

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `.github/workflows/deploy.yml`

- [ ] **Step 1: Add a workflow lint check before editing**

Expected behavior:
- CI runs backend tests with Python 3.12 after installing `backend/requirements.txt`.
- CI runs frontend tests and build with Node 22 using `npm ci`.
- Deploy only runs after the CI workflow succeeds for `main`.

- [ ] **Step 2: Add the CI workflow**

```yaml
name: CI

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: backend/requirements.txt
      - run: python -m pip install --upgrade pip
      - run: pip install -r requirements.txt
      - run: python -m pytest -q

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm test
      - run: npm run build
```

- [ ] **Step 3: Gate deploy on successful CI**

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types:
      - completed
  workflow_dispatch:

jobs:
  deploy:
    if: ${{ github.event_name == 'workflow_dispatch' || (github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'main') }}
```

- [ ] **Step 4: Validate the YAML shape**

Run a YAML parser against both workflow files and verify both load successfully.

### Task 3: Verify repository health

**Files:**
- Review: `.github/workflows/ci.yml`
- Review: `.github/workflows/deploy.yml`
- Review: `backend/tests/test_mvp.py`
- Review: `backend/app/services.py`

- [ ] **Step 1: Run backend tests**

Run: `python -m pytest -q`

- [ ] **Step 2: Run frontend tests**

Run: `npm test`

- [ ] **Step 3: Run frontend build**

Run: `npm run build`

- [ ] **Step 4: Record any environment-only blockers separately from code defects**
