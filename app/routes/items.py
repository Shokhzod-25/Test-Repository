from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import db_helper
from app.models import Items
from app.schemas import Item

router = APIRouter()

@router.post('/item')
async def create_item(item: Item, session: AsyncSession = Depends(db_helper.session_dependency)):
    new_item = Items(title=item.title, description=item.description)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item

@router.get('/item/{item_id}')
async def get_item(item_id: int, session: AsyncSession = Depends(db_helper.session_dependency)):
    return await session.get(Items, item_id)

@router.get('/items')
async def get_items(session: AsyncSession = Depends(db_helper.session_dependency)):
    items = await session.execute(select(Items))
    return items.scalars().all()
