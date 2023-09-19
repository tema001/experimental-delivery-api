from fastapi import APIRouter, Depends, WebSocket, status
import asyncio

from orders.application.query import OrderQueries
from orders.infra.repository import OrderRepository
from api.schemas import OrderResponse, UserOrderResponse, OrderPagesResponse
from orders.application.utils import check_new_events
from exceptions import OrderNotFoundException, NoPermissionByRole
from user.application.service import UserService
from user.domain.entity import AuthorizedUserEntity

from orders.application.commands import OrderCommands
from orders.domain.schemas import OrderReq, OrderUpdate

from uuid import UUID

router = APIRouter(prefix='/orders')


@router.post('/new', status_code=status.HTTP_201_CREATED)
async def new_order(order: OrderReq,
                    user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                    order_command: OrderCommands = Depends()):
    order = await order_command.create_new(order)
    return {'order_id': order.id}


@router.get('/my', response_model=list[UserOrderResponse])
async def get_user_orders(user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                          order_query: OrderQueries = Depends()):
    orders = await order_query.get_orders_by_username(user.username)
    return orders


@router.get('/all', response_model=OrderPagesResponse)
async def get_all_orders(page: int = 1,
                         user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                         order_query: OrderQueries = Depends()):
    UserService.is_rw_access(user)

    orders = await order_query.get_by_pages(page)
    has_more = False
    if len(orders) > 10:
        has_more = True
        orders.pop(-1)

    return {'orders': orders, 'has_more': has_more}


@router.get('/{order_id}', response_model=OrderResponse)
async def get_order(order_id: UUID,
                    user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                    order_repo: OrderRepository = Depends()):
    order = await order_repo.get_by_id(order_id)
    if order is None:
        raise OrderNotFoundException

    if order.customer_name == user.username or UserService.is_rw_access(user):
        return order
    else:
        raise NoPermissionByRole


@router.patch('/{order_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_order(order_id: UUID,
                       order: OrderUpdate,
                       user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                       order_command: OrderCommands = Depends()):
    if not UserService.is_rw_access(user):
        raise NoPermissionByRole

    await order_command.update(order_id, order)


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
                      user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                      order_command: OrderCommands = Depends()):
    UserService.is_rw_access(user)
    async with order_command.wrapper(order_id) as order:
        order.begin()


@router.post('/{order_id}/ready', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_ready(order_id: UUID,
                         user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                         order_command: OrderCommands = Depends()):
    UserService.is_rw_access(user)
    async with order_command.wrapper(order_id) as order:
        order.ready()


@router.post('/{order_id}/delivery', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_delivering(order_id: UUID,
                              user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                              order_command: OrderCommands = Depends()):
    UserService.is_rw_access(user)
    async with order_command.wrapper(order_id) as order:
        order.delivery()


@router.post('/{order_id}/complete', status_code=status.HTTP_204_NO_CONTENT)
async def complete_order(order_id: UUID,
                         user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                         order_command: OrderCommands = Depends()):
    UserService.is_rw_access(user)
    async with order_command.wrapper(order_id) as order:
        order.complete()


@router.post('/{order_id}/cancel', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID,
                       user: AuthorizedUserEntity = Depends(UserService.get_user_from_token),
                       order_command: OrderCommands = Depends()):
    UserService.is_rw_access(user)
    async with order_command.wrapper(order_id) as order:
        order.cancel()
