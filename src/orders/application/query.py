from typing import Any, Sequence
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session
from models import OrderEvent, Order


class OrderQueries:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def get_statuses(self, order_id: UUID) -> list:
        stmt = select(OrderEvent.name, OrderEvent.created_at).where(OrderEvent.order_id == order_id)
        res = await self._db.stream(stmt)

        return [jsonable_encoder(event) async for event in res.mappings()]

    async def get_orders_by_username(self, username: str) -> Sequence[Order]:
        stmt = select(Order).where(Order.customer_name == username).\
                             order_by(Order.created_at.desc())
        res = await self._db.execute(stmt)

        return res.scalars().all()

    async def get_by_pages(self, page: int) -> Sequence[Order]:
        offset = (page - 1) * 10
        limit = offset + 11
        stmt = select(Order).offset(offset).limit(limit).order_by(Order.updated_at.desc())
        res = await self._db.execute(stmt)

        return res.scalars().all()
