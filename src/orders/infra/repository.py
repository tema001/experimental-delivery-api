from datetime import datetime

from fastapi import Depends
from sqlalchemy import insert, select, update

from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session
from models import DeliveryInfo, Order

from shared.infra.repository import GenericRepository

from orders.domain.entity import OrderEntity, DeliveryInfoEntity
from .event_store import OrderEventStore

from uuid import UUID

from ..domain.value_obj import OrderItem


class OrderDataMapper:
    @staticmethod
    def model_to_entity(instance: Order):
        info = instance.delivery_info
        return OrderEntity(id=instance.id,
                           customer_name=instance.customer_name,
                           delivery_info=DeliveryInfoEntity(id=info.id,
                                                            address=info.address,
                                                            courier_id=info.courier_id),
                           order_items=[OrderItem(**x) for x in instance.data['products']],
                           total_price=instance.data.get('total_price', 0.0),
                           status=instance.order_status,
                           created_at=instance.created_at,
                           updated_at=instance.updated_at)

    @staticmethod
    def entity_to_model(entity: OrderEntity):
        info = entity.delivery_info
        return Order(id=entity.id,
                     customer_name=entity.customer_name,
                     delivery_info=DeliveryInfo(id=info.id,
                                                address=info.address,
                                                courier_id=info.courier_id),
                     data=entity.items_as_model_data,
                     order_status=entity.status)


class OrderRepository(GenericRepository):

    def __init__(self,
                 event_store: OrderEventStore = Depends(),
                 db: AsyncSession = Depends(get_session)):
        self.event_store = event_store
        self._db = db

    def map_model(self, instance: Order) -> OrderEntity:
        return OrderDataMapper.model_to_entity(instance)

    def map_entity(self, entity: OrderEntity) -> Order:
        return OrderDataMapper.entity_to_model(entity)

    async def commit(self):
        await self._db.commit()

    async def get_by_id(self, _id: UUID) -> Order | None:
        order_stmt = select(Order).where(Order.id == _id)
        res = await self._db.execute(order_stmt)
        order = res.scalar_one_or_none()

        return order

    async def add(self, entity: OrderEntity):
        await self._add_delivery_info(entity.delivery_info)

        stmt = insert(Order).values(id=entity.id,
                                    customer_name=entity.customer_name,
                                    delivery_info_id=entity.delivery_info.id,
                                    order_status=entity.status,
                                    data=entity.items_as_model_data,
                                    created_at=entity.created_at,
                                    updated_at=entity.updated_at)
        await self._db.execute(stmt)

        await self.event_store.save(entity.events)

    async def change_order_data(self, entity: OrderEntity):
        stmt = update(Order).where(Order.id == entity.id).values(data=entity.items_as_model_data,
                                                                 updated_at=entity.updated_at)
        await self._db.execute(stmt)
        await self.event_store.save(entity.events)

    async def change_delivery_info(self, entity: DeliveryInfoEntity):
        stmt = update(DeliveryInfo).\
                    where(DeliveryInfo.id == entity.id).\
                    values(address=entity.address,
                           courier_id=entity.courier_id)
        await self._db.execute(stmt)

    async def change_status(self, entity: OrderEntity):
        stmt = update(Order). \
            where(Order.id == entity.id). \
            values(order_status=entity.status,
                   updated_at=entity.updated_at)
        await self._db.execute(stmt)
        await self.event_store.save(entity.events)

    async def _add_delivery_info(self, entity: DeliveryInfoEntity):
        stmt = insert(DeliveryInfo).values(**entity.__dict__)
        await self._db.execute(stmt)
