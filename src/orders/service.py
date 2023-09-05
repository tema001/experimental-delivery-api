from datetime import datetime

from fastapi import Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import insert, select, values, update, delete, Integer
from sqlalchemy.sql import column
from sqlalchemy.sql.functions import sum as func_sum
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models import User, Product, DeliveryInfo, Order, OrderItem, OrderStatus
from .schemas import OrderCreate, Status, OrderUpdate

from user.service import get_token_data, verify_rw

from typing import Mapping, Sequence
from db_config import get_session


async def commit_order_status(order_id: int,
                              order_status: str,
                              db: AsyncSession):
    created_status = OrderStatus(order_id=order_id, timestampz=datetime.utcnow(), status=order_status)
    db.add(created_status)
    await db.commit()


async def create_delivery_info(order: OrderCreate,
                               db: AsyncSession = Depends(get_session)) -> int:
    stmt = insert(DeliveryInfo).returning(DeliveryInfo.id).values(address=order.address)
    res = await db.execute(stmt)
    return res.scalar()


async def create_order_items(items: list,
                             order_id: int,
                             db: AsyncSession):
    a = values(
        column('product_id', Integer), column('order_id', Integer), column('quantity', Integer), name='A'
    ).data(
        [(item.id, order_id, item.quantity) for item in items]
    )

    to_select = [a.c.product_id, a.c.order_id, a.c.quantity, Product.price]
    select_stmt = select(*to_select).join_from(Product, a, Product.id == a.c.product_id)

    stmt = insert(OrderItem).from_select(to_select, select_stmt)
    await db.execute(stmt)


async def create_order(order: OrderCreate,
                       db: AsyncSession = Depends(get_session)) -> int:
    delivery_id = await create_delivery_info(order, db)

    sub_stmt = select(User.id).where(User.username == order.customer_name).scalar_subquery()
    stmt = insert(Order).returning(Order.id).values(user_id=sub_stmt,
                                                    delivery_info_id=delivery_id,
                                                    total_price=0,
                                                    created_at=datetime.utcnow())

    try:
        res = await db.execute(stmt)
        new_order_id = res.scalar()
    except IntegrityError as e:
        if 'null value in column "user_id"' in e.args[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Incorrect username'
            )
    await create_order_items(order.items, new_order_id, db)

    total_price_stmt = select(func_sum(OrderItem.price * OrderItem.quantity)). \
                               where(OrderItem.order_id == new_order_id).scalar_subquery()
    update_stmt = update(Order).where(Order.id == new_order_id).values(total_price=total_price_stmt)
    await db.execute(update_stmt)

    await commit_order_status(new_order_id, Status.CREATED, db)
    return new_order_id


async def update_order(order_id: int,
                       order: OrderUpdate,
                       db: AsyncSession = Depends(get_session)) -> int:
    if order.items:
        delete_stmt = delete(OrderItem).where(OrderItem.order_id == order_id)
        await db.execute(delete_stmt)
        await create_order_items(order.items, order_id, db)

        total_price_stmt = select(func_sum(OrderItem.price * OrderItem.quantity)). \
                                where(OrderItem.order_id == order_id).scalar_subquery()
        update_stmt = update(Order).where(Order.id == order_id).values(total_price=total_price_stmt)
        await db.execute(update_stmt)

    if order.address:
        delivery_id_stmt = select(Order.delivery_info_id).where(Order.id == order_id).scalar_subquery()
        update_stmt = update(DeliveryInfo).where(DeliveryInfo.id == delivery_id_stmt).values(address=order.address)
        await db.execute(update_stmt)

    await db.commit()

    return order_id


async def get_detailed_order_by_id(order_id: int,
                                   db: AsyncSession = Depends(get_session)) -> Mapping | None:
    customer_name = User.username.label('customer_name')
    order_stmt = select(Order.id, customer_name, DeliveryInfo.address, OrderStatus.status, OrderStatus.timestampz, Order.total_price). \
                    where(Order.id == order_id). \
                    join(User, User.id == Order.user_id). \
                    join(DeliveryInfo, DeliveryInfo.id == Order.delivery_info_id). \
                    join(OrderStatus, OrderStatus.order_id == Order.id). \
                    order_by(OrderStatus.timestampz.desc()). \
                    limit(1)

    res = await db.execute(order_stmt)
    return res.mappings().first()


async def get_detailed_orders(limit: int = 50,
                              offset: int = 0,
                              db: AsyncSession = Depends(get_session)) -> Sequence[Mapping]:
    customer_name = User.username.label('customer_name')
    orders_stmt = select(Order.id, customer_name, DeliveryInfo.address, OrderStatus.status, OrderStatus.timestampz, Order.total_price). \
                    join(User, User.id == Order.user_id). \
                    join(DeliveryInfo, DeliveryInfo.id == Order.delivery_info_id). \
                    join(OrderStatus, OrderStatus.order_id == Order.id). \
                    distinct(Order.id). \
                    order_by(Order.id.desc(), OrderStatus.timestampz.desc()). \
                    cte()

    final_stmt = select(orders_stmt).order_by(orders_stmt.c.timestampz.desc()).limit(limit).offset(offset)

    res = await db.execute(final_stmt)
    return res.mappings().all()


async def get_order_items(order_id: int,
                          db: AsyncSession = Depends(get_session)) -> Sequence[Mapping]:
    if isinstance(order_id, int):
        order_id = (order_id, )

    order_items_stmt = select(OrderItem.order_id, Product.id, Product.product_name, OrderItem.quantity, OrderItem.price). \
                        where(OrderItem.order_id.in_(order_id)). \
                        join(Product, Product.id == OrderItem.product_id)

    res = await db.execute(order_items_stmt)
    return res.mappings().all()


async def get_detailed_order_list(orders: list = Depends(get_detailed_orders),
                                  db: AsyncSession = Depends(get_session)):
    _orders = [jsonable_encoder(x) for x in orders]

    orders_hmap = {x['id']: x for x in _orders}
    all_items = await get_order_items(orders_hmap.keys(), db)
    for item in all_items:
        _order: dict = orders_hmap.get(item['order_id'])
        if _items := _order.get('items'):
            _items.append(item)
        else:
            _order['items'] = [item]

    return _orders


async def get_orders_by_username(token_data: dict = Depends(get_token_data),
                                 db: AsyncSession = Depends(get_session)) -> Sequence[Mapping]:
    username = token_data['username']
    customer_id_stmt = select(User.id).where(User.username == username).scalar_subquery()

    orders_stmt = select(Order.id, OrderStatus.status, OrderStatus.timestampz, Order.total_price). \
                        where(Order.user_id == customer_id_stmt). \
                        join(OrderStatus, OrderStatus.order_id == Order.id). \
                        distinct(Order.id). \
                        order_by(Order.id.desc(), OrderStatus.timestampz.desc()). \
                        cte()

    final_stmt = select(orders_stmt).order_by(orders_stmt.c.timestampz.desc())

    res = await db.execute(final_stmt)
    return res.mappings().all()


async def test1(order_id: int):
    from contextlib import asynccontextmanager

    async with asynccontextmanager(get_session)() as db:
        while True:
            res = await get_all_order_statuses(order_id, db)
            yield [jsonable_encoder(x) for x in res]


async def get_all_order_statuses(order_id: int,
                                 db: AsyncSession = Depends(get_session)) -> Sequence[Mapping]:
    stmt = select(OrderStatus.status, OrderStatus.timestampz). \
            where(OrderStatus.order_id == order_id). \
            order_by(OrderStatus.timestampz.asc())

    res = await db.execute(stmt)
    return res.mappings().all()


class SetStatus:
    def __init__(self, current: Status, new: Status):
        self.current = current
        self.new = new

    async def __call__(self,
                       order_id: int,
                       access: bool = Depends(verify_rw),
                       statuses: list[Mapping] = Depends(get_all_order_statuses),
                       db: AsyncSession = Depends(get_session)) -> Status | None:
        order_status = statuses[-1]['status']
        if order_status is None or order_status == Status.CANCELED or order_status == Status.COMPLETED:
            return
        if order_status == self.current or self.current == Status.ANY:
            await commit_order_status(order_id, self.new, db)
            order_status = self.new

        return order_status


set_start_status = SetStatus(Status.CREATED, Status.STARTED)
set_ready_status = SetStatus(Status.STARTED, Status.READY_TO_DELIVERY)
set_delivering_status = SetStatus(Status.READY_TO_DELIVERY, Status.DELIVERING)
set_complete_status = SetStatus(Status.DELIVERING, Status.COMPLETED)
set_cancel_status = SetStatus(Status.ANY, Status.CANCELED)
