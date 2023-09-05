from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    product_name: str
    price: float
