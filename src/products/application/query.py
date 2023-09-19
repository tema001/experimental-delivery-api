from typing import Sequence

from fastapi import Depends

from products.domain.entity import ProductEntity
from products.infra.repository import ProductRepository


class ProductQuery:

    def __init__(self, repo: ProductRepository = Depends()):
        self.repo = repo

    async def get_product(self, product_id: int) -> ProductEntity:
        return await self.repo.get_by_id(product_id)

    async def get_category_products(self, category_name: str) -> Sequence[ProductEntity]:
        return await self.repo.get_products_by_category_name(category_name)
