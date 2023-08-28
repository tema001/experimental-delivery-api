from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
import asyncio

from . import service
from .schemas import OrderResponse, Status
from .utils import check_new_events
from exceptions import OrderNotFoundException, OrderStatusTransitionError
from auth.service import verify_rw

from typing import Mapping

router = APIRouter(prefix='/orders')


@router.post('/new', status_code=status.HTTP_201_CREATED)
async def new_order(order_resp: int = Depends(service.create_order)):
    return {'order_id': order_resp}


@router.patch('/{order_id}')
async def update_order(perm: bool = Depends(verify_rw),
                       resp: int = Depends(service.update_order)):
    return {'order_id': resp}


@router.get('/list')
async def get_user_orders(orders: list[Mapping] = Depends(service.get_orders_by_username)):
    return orders


@router.get('/all')
async def get_all_orders(perm: bool = Depends(verify_rw),
                         orders: list[Mapping] = Depends(service.get_detailed_order_list)):
    return orders


@router.get('/{order_id}')
async def get_order(order: Mapping = Depends(service.get_detailed_order_by_id),
                    order_items: Mapping = Depends(service.get_order_items)):
    if order is None:
        raise OrderNotFoundException()

    return OrderResponse(**order, items=order_items)


@router.websocket("/{order_id}/ws")
async def websocket_endpoint(order_id: int,
                             websocket: WebSocket):
    get_statuses = service.test1(order_id)
    statuses = await anext(get_statuses)

    if len(statuses) == 0:
        raise OrderNotFoundException()

    try:
        await websocket.accept()
        cache = None
        while True:
            await asyncio.wait_for(websocket.send_text('ping'), timeout=2.0)
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
            assert msg == 'pong'

            statuses = await anext(get_statuses)
            new_statuses = check_new_events(statuses, cache)

            if new_statuses:
                await websocket.send_json(new_statuses)
                cache = statuses

            await asyncio.sleep(10)
    finally:
        await get_statuses.aclose()
        await websocket.close()


def order_status_verification(actual: Status, expected: Status):
    if not actual:
        raise OrderNotFoundException()
    elif actual != expected:
        raise OrderStatusTransitionError(actual, expected)


@router.post('/{order_id}/begin', status_code=status.HTTP_204_NO_CONTENT)
async def begin_order(order_status: Status = Depends(service.set_start_status)):
    order_status_verification(order_status, Status.STARTED)


@router.post('/{order_id}/ready', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_ready(order_status: Status = Depends(service.set_ready_status)):
    order_status_verification(order_status, Status.READY_TO_DELIVERY)


@router.post('/{order_id}/delivery', status_code=status.HTTP_204_NO_CONTENT)
async def order_is_delivering(order_status: Status = Depends(service.set_delivering_status)):
    order_status_verification(order_status, Status.DELIVERING)


@router.post('/{order_id}/complete', status_code=status.HTTP_204_NO_CONTENT)
async def complete_order(order_status: Status = Depends(service.set_complete_status)):
    order_status_verification(order_status, Status.COMPLETED)


@router.post('/{order_id}/cancel', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_status: Status = Depends(service.set_cancel_status)):
    order_status_verification(order_status, Status.CANCELED)
