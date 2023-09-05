from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    name: str
    quantity: int
    price: float
