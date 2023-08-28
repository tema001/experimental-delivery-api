from typing import Mapping

from fastapi import APIRouter, Depends

from .schemas import ProductResponse
from .service import get_category_products, get_product_by_id

from exceptions import ProductNotFoundException

router = APIRouter()


@router.get('/category/{category_name}')
async def products_by_category(products: list = Depends(get_category_products)):
    return products


@router.get('/product/{product_id}', response_model=ProductResponse)
async def get_product(product: Mapping = Depends(get_product_by_id)):
    if not product:
        raise ProductNotFoundException()

    return product
