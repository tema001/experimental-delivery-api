from dataclasses import dataclass
from enum import Enum

from uuid import UUID


@dataclass(frozen=True)
class OrderItem:
    product_id: UUID
    name: str
    quantity: int
    price: float

    def as_dict(self) -> dict:
        res = self.__dict__.copy()
        res['product_id'] = str(self.product_id)
        return res


class Status(str, Enum):
    CREATED = 'CREATED'
    STARTED = 'STARTED'
    READY_TO_DELIVERY = 'READY_TO_DELIVERY'
    DELIVERING = 'DELIVERING'
    COMPLETED = 'COMPLETED'

    CANCELED = 'CANCELED'

    def __str__(self):
        return self.value
