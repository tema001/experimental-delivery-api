from datetime import datetime

from pydantic import BaseModel, Field
from uuid import UUID


class ProductResponse(BaseModel):
    id: UUID
    product_name: str
    price: float


class DeliveryInfoResponse(BaseModel):
    id: UUID
    address: str
    courier_id: UUID | None = None

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: UUID
    customer_name: str
    data: dict
    delivery_info: DeliveryInfoResponse
    order_status: str
    created_at: datetime

    class Config:
        orm_mode = True
