from shared.domain.entity import Entity
from dataclasses import dataclass


@dataclass
class ProductEntity(Entity):
    product_name: str
    price: float
    category_name: str = None
