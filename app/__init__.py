from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import db_helper
from app.routes.items import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.init_database()
    yield

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app

