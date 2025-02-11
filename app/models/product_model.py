from app.models.models import Product, ProductImage
from pydantic import BaseModel, Field
from enum import Enum

class ProductRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)
    price: int = Field(..., ge=0)
    user_id: int = Field(..., ge=0)
    category_id: int = Field(..., ge=0)

class ProductResponse(BaseModel):
    product: Product
    productImages: list[ProductImage]

class ProductSortType(Enum):
    ACCURACY = 0
    LATEST = 1