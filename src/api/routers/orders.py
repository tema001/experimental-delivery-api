from fastapi import APIRouter, Depends, WebSocket, status
import asyncio

from orders import service
from orders.application.query import OrderQueries
from orders.infra.repository import OrderRepository
from api.schemas import OrderResponse
from orders.application.utils import check_new_events
from exceptions import OrderNotFoundException
from user.service import verify_rw

from orders.application.commands import OrderCommands
from orders.domain.schemas import OrderReq, OrderUpdate

from typing import Mapping
from uuid import UUID

router = APIRouter(prefix='/orders')


@router.get('/{order_id}', response_model=OrderResponse)
async def get_order(order_id: UUID,
                    order_repo: OrderRepository = Depends()):
    order = await order_repo.get_by_id(order_id)
    if order is None:
        raise OrderNotFoundException()

    return order


@router.post('/new', status_code=status.HTTP_201_CREATED)
async def new_order(order: OrderReq,
                    order_command: OrderCommands = Depends()):
    order = await order_command.create_new(order)
    return {'order_id': order.id}


@router.patch('/{order_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_order(order_id: UUID,
                       order: OrderUpdate,
                       order_command: OrderCommands = Depends()):
    await order_command.update(order_id, order)


@router.get('/list')
async def get_user_orders(orders: list[Mapping] = Depends(service.get_orders_by_username)):
    return orders


@router.get('/all')
async def get_all_orders(perm: bool = Depends(verify_rw),
                         orders: list[Mapping] = Depends(service.get_detailed_order_list)):
    return orders


@router.websocket("/{order_id}/ws")
async def websocket_endpoint(order_id: UUID,
                             websocket: WebSocket,
                             order_query: OrderQueries = Depends()):
    statuses = await order_query.get_statuses(order_id)

    if len(statuses) == 0:
        raise OrderNotFoundException()

    try:
        await websocket.accept()
        cache = None
        while True:
            await asyncio.wait_for(websocket.send_text('ping'), timeout=2.0)
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
            assert msg == 'pong'

            statuses = await order_query.get_statuses(order_id)
            new_statuses = check_new_events(statuses, cache)

            if new_statuses:
                await websocket.send_json(new_statuses)
                cache = statuses

            await asyncio.sleep(10)
    finally:
        await websocket.close()


@router.post('/{order_id}/begin', status_code=status.HTTP_204_NO_CONTENT)
async def begin_order(order_id: UUID,
                      order_command: OrderCommands = Depends()):
    async with order_command.wrapper(order_id) as order:
        order.begin()


@router.post('/{order_id}/ready', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_ready(order_id: UUID,
                         order_command: OrderCommands = Depends()):
    async with order_command.wrapper(order_id) as order:
        order.ready()


@router.post('/{order_id}/delivery', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_delivering(order_id: UUID,
                              order_command: OrderCommands = Depends()):
    async with order_command.wrapper(order_id) as order:
        order.delivery()


@router.post('/{order_id}/complete', status_code=status.HTTP_204_NO_CONTENT)
async def complete_order(order_id: UUID,
                         order_command: OrderCommands = Depends()):
    async with order_command.wrapper(order_id) as order:
        order.complete()


@router.post('/{order_id}/cancel', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID,
                       order_command: OrderCommands = Depends()):
    async with order_command.wrapper(order_id) as order:
        order.cancel()
