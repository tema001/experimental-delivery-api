from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session
from models import OrderEvent


class OrderQueries:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def get_statuses(self, order_id: UUID):
        stmt = select(OrderEvent.name, OrderEvent.created_at).where(OrderEvent.order_id == order_id)
        res = await self._db.stream(stmt)

        return [jsonable_encoder(event) async for event in res.mappings()]
