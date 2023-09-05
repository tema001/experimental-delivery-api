from typing import Mapping, Sequence

from fastapi import Depends

from shared.domain.entity import Entity
from shared.infra.repository import GenericRepository
from products.domain.entity import ProductEntity

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session

from models import Category, Product


class ProductDataMapper:
    @staticmethod
    def model_to_entity(instance: Mapping):
        return ProductEntity(**instance)

    @staticmethod
    def entity_to_model(entity: ProductEntity):
        return Product(**entity.__dict__)


class ProductRepository(GenericRepository):

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self._db = db

    async def get_by_id(self, _id: int) -> ProductEntity | None:
        stmt = select(Product.id, Product.product_name, Product.price, Category.category_name) \
            .join(Category).where(Product.id == _id)
        res = await self._db.execute(stmt)
        res = res.mappings().one_or_none()

        if res is None:
            return res
        return self.map_model_to_entity(res)

    async def get_products_by_category_name(self, category_name: str) -> Sequence:
        category_id_stms = select(Category.id).where(Category.category_name == category_name).scalar_subquery()
        stmt = select(Product.id, Product.product_name, Product.price).where(Product.category_id == category_id_stms)
        res = await self._db.execute(stmt)
        res = res.mappings().all()

        return self.map_model_to_entity(res)

    async def add(self, entity: Entity):
        pass

    def map_model_to_entity(self, instance: Mapping | Sequence) -> ProductEntity | Sequence:
        if isinstance(instance, Sequence):
            return [ProductDataMapper.model_to_entity(x) for x in instance]

        return ProductDataMapper.model_to_entity(instance)


