import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn

from fastapi import APIRouter, FastAPI, Depends, HTTPException

from pydantic import BaseModel

from redis.asyncio import Redis

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Integer, String, Text, select


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.init_database()
    yield


def create_app():
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    return app

class Database:
    def __init__(self):
        self.engine = create_async_engine(url="postgresql+asyncpg://myuser:mypassword@localhost:5433/mydatabase")
        self.session_factory = async_sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def init_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

class RedisClient:
    def __init__(self):
        self.redis = Redis()

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 60):
        await self.redis.setex(key, ttl, value)

db_helper = Database()
redis_client = RedisClient()

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
class Items(Base):
    __tablename__ = 'items'
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)

router = APIRouter()

class Item(BaseModel):
    title: str
    description: str

@router.post('/item')
async def create_item(item: Item, session: AsyncSession = Depends(db_helper.session_dependency)):
    new_item = Items(title=item.title, description=item.description)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item



@router.get('/item/{item_id}')
async def get_item(item_id: int):
    item = await redis_client.get(f'item_{item_id}')

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return json.loads(item)


@router.get('/items')
async def get_items(session: AsyncSession = Depends(db_helper.session_dependency)):
    items = await session.execute(select(Items))
    items = items.scalars().all()
    [await redis_client.set(f'item_{item.id}', str(json.dumps({item.title: item.description}))) for item in items]
    return items

if __name__ == '__main__':
    uvicorn.run("main:create_app", reload=True, factory=True)
