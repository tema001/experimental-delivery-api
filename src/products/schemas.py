from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    product_name: str
    price: float
    category_name: str = None

    class Config:
        orm_mode = True

