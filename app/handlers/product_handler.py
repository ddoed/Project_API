from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Path, Body
from app.dependencies import get_db_session
from app.models.models import *
from app.models.product_model import *
from app.services.product_service import ProductService
from sqlmodel import Session, select

router = APIRouter(
    prefix="/products"
)

# 물건에 좋아요 추가
@router.post("/products/{product_id}/likes")
def post_product_likes_add(product_id: int, like_request: user_LikeRequest, db: Session = Depends(get_db_session)):
    user_id = like_request.user_id  # JSON body에서 user_id를 추출

    # 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        #상품이 없는경우, 에러 메세지 출력
        raise HTTPException(status_code=404, detail="Product not found")

    # 사용자가 이미 이 상품을 좋아요 한 적이 있는지 확인
    # * Likes 테이블에서 user.id와 product.id가 모두 동일한 값이 있는지 확인
    existing_like = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    if existing_like:
        # 이미 있는 경우, 에러 메세지 출력
        raise HTTPException(status_code=400, detail="You already liked this product")

    # 좋아요 추가
    new_like = Likes(user_id=user_id, product_id=product_id)
    db.add(new_like)
    db.commit()
    # 새로운 객체가 추가되어 데이터베이스에 남아 있으므로 refresh 수행
    db.refresh(new_like)

    return {"message": "Like added successfully", "like_id": new_like.id, "liker_id": new_like.user_id}

# 좋아요 누른 물건 좋아요 삭제
@router.delete("/products/{product_id}/likes")
def delete_product_likes(product_id: int, delete_request: user_LikeRequest, db: Session = Depends(get_db_session)):
    user_id = delete_request.user_id

    # 사용자가 해당 상품에 좋아요를 눌렀는지 확인
    like_to_delete = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    # 좋아요 한 적이 없는 경우 에러 메세지 출력
    if not like_to_delete:
        raise HTTPException(status_code=404, detail="Like not found.")
    
    # 좋아요 삭제
    db.delete(like_to_delete)
    db.commit()

    return {"message": "Like deleted successfully", "like_id": like_to_delete.id, "liker_id": like_to_delete.user_id}
    
@router.get("/", status_code=200)
def get_products(q: Optional[str] = Query(None),
                 category_id: Optional[int] = Query(None),
                 soldout: Optional[bool] = Query(None),
                 min_price: Optional[int] = Query(None, ge=0),
                 max_price: Optional[int] = Query(None, ge=0),
                 sort_type: int = Query(ProductSortType.ACCURACY),
                 page: int = Query(0, ge=0),
                 limit: int = Query(10, le=100),
                 db: Session = Depends(get_db_session),
                 productService: ProductService = Depends()
) -> list[ProductResponse]:
    products = productService.get_products(db, q, category_id, soldout, min_price, max_price, sort_type, page, limit)
    productImagesList = [
        productService.get_product_images(db, product.id) for product in products
    ]
    result = map(
            lambda product, productImages: ProductResponse(product=product, productImages=productImages),
            products, productImagesList
    )
    return list(result)

@router.post("/", status_code=201)
def create_product(productRequest: ProductRequest = Body(...),
                         db: Session = Depends(get_db_session),
                         productService: ProductService = Depends()
) -> ProductResponse:
    product = productService.create_product(db, productRequest)
    return ProductResponse(product=product, productImages=[])

@router.get("/{product_id}", status_code=200)
def get_product(product_id: int = Path(..., ge=0),
                db: Session = Depends(get_db_session),
                productService: ProductService = Depends()
) -> ProductResponse:
    product = productService.get_product(db, product_id)
    productImage = productService.get_product_images(db, product_id)
    return ProductResponse(product=product, productImages=productImage)

@router.put("/{product_id}", status_code=200)
def update_product(product: ProductRequest = Body(...),
                   product_id: int = Path(..., ge=0),
                   db: Session = Depends(get_db_session),
                   productService: ProductService = Depends()) -> ProductResponse:
    product = productService.update_product(db, product_id, product)
    productImage = productService.get_product_images(db, product_id)
    return ProductResponse(product=product, productImages=productImage)

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int = Path(..., ge=0),
                   db: Session = Depends(get_db_session),
                   productService: ProductService = Depends()) -> None:
    # !: Product 삭제 전에 Product와 연결되어 있는 테이블들에서도 삭제해줘야함..
    # => sol 1. DELETE /products/{product_id}에서 각 테이블에 대한 DELETE API를 호출
    # => sol 2. DB에서 CASCADE 설정 => 자동으로 연결된 테이블에서도 삭제
    # 의논해봐야 할 듯.
    productService.delete_all_product_images(db, product_id)
    productService.delete_product(db, product_id)
    return None

# !: 업로드 된 image를 가져오기 위하여
# GET /products/{product_id}/images{image_id} 이런 것도 필요할 듯
# TODO: 
@router.get("/{product_id}/image/{image_id}", status_code=200)
def get_product_image(product_id: int = Path(..., ge=0),
                      image_id: int = Path(..., ge=0),
                      db: Session = Depends(get_db_session),
                      productService: ProductService = Depends()
) -> ProductImage:
    # return productService.get_product_image(db, product_id, image_id)
    raise NotImplementedError()

@router.post("/{product_id}/image", status_code=200)
async def upload_product_image(product_id: int = Path(..., ge=0),
                         image: UploadFile = File(...),
                         db: Session = Depends(get_db_session),
                         productService: ProductService = Depends()
) -> ProductImage:
    return await productService.upload_product_image(db, product_id, image)

@router.delete("/{product_id}/image/{image_id}", status_code=204)
def delete_product_image(product_id: int = Path(..., ge=0),
                         image_id: int = Path(..., ge=0),
                         db: Session = Depends(get_db_session),
                         productService: ProductService = Depends()
) -> None:
    productService.delete_product_image(db, product_id, image_id)
    return None