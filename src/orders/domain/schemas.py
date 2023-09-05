from datetime import datetime

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    price: float
    quantity: int


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    items: list[OrderItemResponse]
    address: str
    status: str
    timestampz: datetime
    total_price: float
