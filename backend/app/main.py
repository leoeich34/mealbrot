from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.inventory.router import router as inventory_router
from app.modules.planner.router import router as planner_router
from app.modules.recipes.router import router as recipes_router
from app.modules.shopping.router import router as shopping_router


app = FastAPI(title="Сервис планирования питания", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth_router,
    admin_router,
    catalog_router,
    inventory_router,
    recipes_router,
    planner_router,
    shopping_router,
):
    app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
