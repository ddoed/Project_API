from app.models.models import Product, ProductImage
from app.dependencies import get_db_session
from fastapi import FastAPI, APIRouter, Depends, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

router = APIRouter(
    prefix="/products",
)

class ProductRequest(BaseModel):
    title: str
    content: str
    price: int
    user_id: int
    category_id: int
    productImages: List[ProductImage]

class ProductResponse(BaseModel):
    product: Product
    productImages: List[ProductImage]

class ProductSortType(Enum):
    ACCURACY = 0
    LATEST = 1
    
@router.get("/", status_code=200)
def get_product_(q: Optional[str] = Query(None),
                 category_id: Optional[int] = Query(None),
                 soldout: Optional[bool] = Query(None),
                 min_price: Optional[int] = Query(None),
                 max_price: Optional[int] = Query(None),
                 sort_type: ProductSortType = Query(ProductSortType.ACCURACY),
                 page: int = Query(0, ge=0),
                 limit: int = Query(10, le=100),
                 session: Session = Depends(get_db_session)) -> List[ProductResponse]:
    raise NotImplementedError()

@router.post("/", status_code=201)
def create_product(productRequest: ProductRequest,
                   session: Session = Depends(get_db_session)) -> ProductResponse:
    raise NotImplementedError()

@router.put("/{product_id}", status_code=200)
def update_product(productRequest: ProductRequest,
                   session: Session = Depends(get_db_session)) -> ProductResponse:
    raise NotImplementedError()

@router.delete("/{product_id}", status_code=200)
def delete_product(product_id: int,
                   session: Session = Depends(get_db_session)) -> None:
    raise NotImplementedError()

@router.get("/{product_id}", status_code=200)
def get_product(product_id: int,
                session: Session = Depends(get_db_session)) -> ProductResponse:
    raise NotImplementedError()

# ?: 업로드 가능한 이미지의 개수에 제한을 둘 것인가?
# ?: 이미지는 한 번에 여러 개 업로드 가능하게 만들 것인가?
@router.put("/{product_id}/image", status_code=200)
def update_product_image(product_id: int,
                         image_URIs: List[str],
                         session: Session = Depends(get_db_session)) -> None:
    raise NotImplementedError()

# !: 문서에서 이미지 제거 라우터 누락됨 => 이미지 제거 라우터 추가
@router.delete("/{product_id}/image", status_code=200)
def delete_product_image(product_id: int,
                         image_id: int,
                         session: Session = Depends(get_db_session)) -> None:
    raise NotImplementedError()