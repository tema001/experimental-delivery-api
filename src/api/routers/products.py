from fastapi import APIRouter, Depends

from api.schemas import ProductResponse
from products.application.query import ProductQuery

from exceptions import ProductNotFoundException

router = APIRouter()


@router.get('/category/{category_name}', response_model=list[ProductResponse])
async def products_by_category(category_name: str,
                               product_query: ProductQuery = Depends(ProductQuery)):
    products = await product_query.get_category_products(category_name)
    return products


@router.get('/product/{product_id}')
async def get_product(product_id: int,
                      product_query: ProductQuery = Depends(ProductQuery)):
    product = await product_query.get_product(product_id)
    if not product:
        raise ProductNotFoundException()

    return product
