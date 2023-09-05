from datetime import datetime
from typing import Mapping

from fastapi import Depends
from sqlalchemy import insert, select

from db_config import get_session
from models import DeliveryInfo, Order, Product

from shared.infra.repository import GenericRepository

from orders.domain.schemas import OrderResponse, OrderItemResponse
from orders.domain.entity import OrderEntity, DeliveryInfoEntity
from orders.domain.value_obj import OrderItem

from sqlalchemy.ext.asyncio import AsyncSession


class OrderDataMapper:
    @staticmethod
    def model_to_entity(instance: Mapping):
        pass


class OrderRepository(GenericRepository):

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db
        self._events = []

    async def get_by_id(self, _id: int):
        order_stmt = select(Order, DeliveryInfo).where(Order.id == _id). \
            join(DeliveryInfo, DeliveryInfo.id == Order.delivery_info_id)

        res = await self._db.execute(order_stmt)
        order = res.scalar_one_or_none()

        return order

    async def add_delivery_info(self, entity: DeliveryInfoEntity):
        stmt = insert(DeliveryInfo).returning(DeliveryInfo.id).values(**entity)
        res = await self._db.execute(stmt)
        entity.id = res.scalar()

    async def add(self, entity: OrderEntity):
        stmt = insert(Order).returning(Order.id).values(customer_name=entity.customer_name,
                                                        delivery_info_id=entity.delivery_info.id,
                                                        order_status=entity.order_status,
                                                        created_at=datetime.utcnow())
        res = await self._db.execute(stmt)
        entity.id = res.scalar()

    async def add_items(self, entity: OrderEntity):
        items_hmap = {x.product_id: x for x in entity.order_items}

        stmt = select(Product.id, Product.product_name, Product.price). \
                    where(Product.id.in_(items_hmap.keys()))

        res = await self._db.execute(stmt)
        products = res.mappings().all()

        new_items = []
        for p in products:
            saved_p = items_hmap[p.get('id')]
            new_items.append({
                'product_id': saved_p.product_id,
                'name': p.get('name'),
                'quantity': saved_p.quantity,
                'price': p.get('price')
            })
