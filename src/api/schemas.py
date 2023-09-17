from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


class ProductResponse(BaseModel):
    id: UUID
    product_name: str
    price: float


class DeliveryAddressResponse(BaseModel):
    address: str

    class Config:
        orm_mode = True


class UserOrderResponse(BaseModel):
    id: UUID
    order_status: str
    data: dict
    created_at: datetime
    updated_at: datetime
    delivery_info: DeliveryAddressResponse

    class Config:
        orm_mode = True


class DeliveryInfoResponse(DeliveryAddressResponse):
    id: UUID
    courier_id: UUID | None = None


class OrderResponse(UserOrderResponse):
    customer_name: str
    delivery_info: DeliveryInfoResponse


class OrderPagesResponse(BaseModel):
    orders: list[OrderResponse]
    has_more: bool
