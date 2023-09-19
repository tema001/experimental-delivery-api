from pydantic import BaseModel
from uuid import UUID


class OrderItemReq(BaseModel):
    id: UUID
    quantity: int


class OrderReq(BaseModel):
    customer_name: str
    items: list[OrderItemReq]
    address: str


class OrderUpdate(BaseModel):
    items: list[OrderItemReq] | None
    address: str | None
