from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models import OrderEvent

from db_config import get_session
from shared.domain.events import DomainEvent


class OrderEventStore:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def save(self, events: list[DomainEvent]):
        if not events:
            return

        self._db.add_all([self.map_to_model(x) for x in events])
        events.clear()

    def map_to_model(self, event: DomainEvent):
        return OrderEvent(id=event.id,
                          order_id=event.aggregate_id,
                          name=event.name,
                          data=event.data,
                          created_at=event.created_at)
