from datetime import datetime

from shared.domain.entity import Entity, AggregateRoot
from .value_obj import OrderItem

from dataclasses import dataclass


@dataclass
class DeliveryInfoEntity(Entity):
    address: str
    courier_id: int


@dataclass
class OrderEntity(AggregateRoot):
    customer_name: str
    delivery_info: DeliveryInfoEntity
    order_items: list[OrderItem]
    total_price: float
    order_status: str
    created_at: datetime
