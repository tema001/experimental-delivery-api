from typing import Mapping, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_config import get_session
from models import Category, Product


async def get_category_products(category_name: str, db: AsyncSession = Depends(get_session)) -> Sequence:
    category_id_stms = select(Category.id).where(Category.category_name == category_name).scalar_subquery()
    stmt = select(Product.id, Product.product_name, Product.price).where(Product.category_id == category_id_stms)
    res = await db.execute(stmt)

    return res.mappings().all()


async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_session)) -> Mapping | None:
    stmt = select(Product.id, Product.product_name, Product.price, Category.category_name)\
            .join(Category).where(Product.id == product_id)
    res = await db.execute(stmt)

    return res.one_or_none()
