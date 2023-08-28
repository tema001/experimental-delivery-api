from datetime import datetime

from pydantic import BaseModel
from enum import Enum


class Status(str, Enum):
    CREATED = 'CREATED'
    STARTED = 'STARTED'
    READY_TO_DELIVERY = 'READY_TO_DELIVERY'
    DELIVERING = 'DELIVERING'
    COMPLETED = 'COMPLETED'

    CANCELED = 'CANCELED'
    ANY = 'ANY'

    def __str__(self):
        return self.value


class OrderItem(BaseModel):
    id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    items: list[OrderItem]
    address: str


class OrderUpdate(BaseModel):
    items: list[OrderItem] | None
    address: str | None


class OrderItemResponse(OrderItem):
    product_name: str
    price: float


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    items: list[OrderItemResponse]
    address: str
    status: Status
    timestampz: datetime
    total_price: float


class OrderStatusResponse(BaseModel):
    status: str
    timestampz: datetime
