from contextlib import asynccontextmanager

from fastapi import Depends

from orders.infra.repository import OrderRepository
from products.infra.repository import ProductRepository
from orders.domain.value_obj import OrderItem
from orders.domain.entity import OrderEntity
from orders.domain.events import AddItemsToOrder
from orders.domain.schemas import OrderReq, OrderItemReq, OrderUpdate

from uuid import UUID

from ..domain.exceptions import OrderNotFoundException


class OrderCommands:

    def __init__(self,
                 order_repo: OrderRepository = Depends(),
                 product_repo: ProductRepository = Depends()):
        self._order_repo = order_repo
        self._product_repo = product_repo

    async def create_new(self, _input: OrderReq) -> OrderEntity:
        items = await self.form_items(_input.items)
        order = OrderEntity.create(_input.customer_name,
                                   _input.address,
                                   items)
        order.calc_total_price()
        order.events.append(AddItemsToOrder(order.id, data=order.items_as_model_data))

        await self._order_repo.add(order)
        await self._order_repo.commit()

        return order

    async def update(self, order_id: UUID, _input: OrderUpdate):
        order = await self._order_repo.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException

        order = self._order_repo.map_model(order)
        if _input.items:
            new_items = await self.form_items(_input.items)
            order.update_items(new_items)
            await self._order_repo.change_order_data(order)

        if _input.address:
            order.update_address(_input.address)
            await self._order_repo.change_delivery_info(order.delivery_info)

        await self._order_repo.commit()

    async def form_items(self, items: list[OrderItemReq]) -> list[OrderItem]:
        items_hmap = {x.id: x for x in items}
        products = await self._product_repo.get_many_by_ids(items_hmap.keys())

        if len(products) != len(items):
            raise

        new_items = []
        for p in products:
            saved_p: OrderItemReq = items_hmap[p.id]
            new_items.append(
                OrderItem(saved_p.id,
                          p.product_name,
                          saved_p.quantity,
                          p.price)
            )
        return new_items

    @asynccontextmanager
    async def wrapper(self, order_id: UUID) -> OrderEntity:
        order = await self._order_repo.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException

        order = self._order_repo.map_model(order)
        yield order

        await self._order_repo.change_status(order)
        await self._order_repo.commit()
