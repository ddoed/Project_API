# app/handlers/product_handler.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, UploadFile, File, Path, Body
from app.db import get_db_session
from app.models.auth_models import *
from app.models.user_and_product_model import *
from app.services.product_service import ProductService
from app.handlers.auth_handler import get_current_user
from sqlmodel import Session, asc, desc, select

router = APIRouter(
    prefix="/products"
)

@router.get("/{product_id}/likes", status_code=200)
def get_product_like_status(product_id: int, user_id: int, db: Session = Depends(get_db_session)):
    """사용자가 특정 상품을 좋아요 했는지 여부 확인"""
    existing_like = db.exec(
        select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)
    ).first()

    return {"liked": existing_like is not None}

# 물건에 좋아요 추가
@router.post("/{product_id}/likes")
def post_product_likes_add(product_id: int, like_request: user_LikeRequest, db: Session = Depends(get_db_session)):
    user_id = like_request.user_id  # JSON body에서 user_id를 추출

    # 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        #상품이 없는경우, 에러 메세지 출력
        raise HTTPException(status_code=404, detail="Product not found")

    # 사용자가 이미 이 상품을 좋아요 한 적이 있는지 확인
    # Likes 테이블에서 user.id와 product.id가 모두 동일한 값이 있는지 확인
    existing_like = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    if existing_like:
        # 이미 있는 경우, 에러 메세지 출력
        raise HTTPException(status_code=400, detail="You already liked this product")

    # 좋아요 추가
    new_like = Likes(user_id=user_id, product_id=product_id)
    db.add(new_like)
    
    # product모델에 좋아요 개수 추가
    product.heart_count += 1
    db.commit()
    # 새로운 객체가 추가되어 데이터베이스에 남아 있으므로 refresh 수행
    db.refresh(new_like)

    return {"message": "Like added successfully", "like_id": new_like.id, "liker_id": new_like.user_id}

# 좋아요 누른 물건 좋아요 삭제
@router.delete("/{product_id}/likes")
def delete_product_likes(product_id: int, delete_request: user_LikeRequest, db: Session = Depends(get_db_session)):
    user_id = delete_request.user_id

    # 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        #상품이 없는경우, 에러 메세지 출력
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 사용자가 해당 상품에 좋아요를 눌렀는지 확인
    like_to_delete = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    # 좋아요 한 적이 없는 경우 에러 메세지 출력
    if not like_to_delete:
        raise HTTPException(status_code=404, detail="Like not found.")
    
    # 좋아요 삭제
    db.delete(like_to_delete)

    # product모델에 좋아요 개수 감소
    product.heart_count -= 1
    db.commit()

    return {"message": "Like deleted successfully", "like_id": like_to_delete.id, "liker_id": like_to_delete.user_id}
    

def validate_product_id(
    product_id: int = Path(..., ge=0),
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends()
) -> Product:
    return productService.get_product(db, product_id)

def validate_product_owner(
    product: Product = Depends(validate_product_id),
    current_user: User = Depends(get_current_user),
) -> Product:
    if current_user.id != product.user_id: # ?: or current_user.role != UserRole.ADMIN,  관리자 권한이 필요하면 추가
        raise HTTPException(status_code=403, detail="User does not have permission.")
    return product

def validate_product_image_owner(
        image_id: int = Path(..., ge=0),
        db: Session = Depends(get_db_session),
        productService: ProductService = Depends(),
        product: Product = Depends(validate_product_owner)
) -> ProductImage:
    return productService.get_product_image(db, product.id, image_id)

class ProductSortType(str, Enum):
    ACCURACY = "accuracy"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    LATEST = "latest"
    LIKES = "likes"

@router.get("/", status_code=200)
def get_products(
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    soldout: Optional[bool] = Query(None),
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    sort_type: ProductSortType = Query(ProductSortType.ACCURACY),
    page: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends()
) -> list[ProductResponse]:

    query = select(Product)

    if q:
        query = query.where(Product.title.contains(q))

    if category_id:
        query = query.where(Product.category_id == category_id)

    if soldout is not None:
        query = query.where(Product.soldout == soldout)

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # 🏷 정렬 기준 적용
    if sort_type == ProductSortType.PRICE_ASC:
        query = query.order_by(asc(Product.price))
    elif sort_type == ProductSortType.PRICE_DESC:
        query = query.order_by(desc(Product.price))
    elif sort_type == ProductSortType.LATEST:
        query = query.order_by(desc(Product.date))
    elif sort_type == ProductSortType.LIKES:
        query = query.order_by(desc(Product.heart_count))
    else:
        query = query.order_by(Product.id)  # 기본값: 등록 순

    products = db.exec(query.offset(page * limit).limit(limit)).all()

    result = [
        ProductResponse(product=product, productImages=productService.get_product_images(db, product.id))
        for product in products
    ]
    
    return result

@router.post("/", status_code=201)
def create_product(
    productRequest: ProductRequest = Body(...),
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    current_user: User = Depends(get_current_user)
) -> ProductResponse:
    product = productService.create_product(db, productRequest, current_user)
    return ProductResponse(product=product, productImages=[])

@router.get("/{product_id}", status_code=200)
def get_product(
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    product: Product = Depends(validate_product_id)
) -> ProductResponse:
    product_images = productService.get_product_images(db, product.id)
    return ProductResponse(product=product, productImages=product_images)

@router.put("/{product_id}", status_code=200)
def update_product(
    productRequest: ProductRequest = Body(...),
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    product: Product = Depends(validate_product_owner)
) -> ProductResponse:
    updated_product = productService.update_product(db, productRequest, product)
    product_images = productService.get_product_images(db, product.id)
    return ProductResponse(product=updated_product, productImages=product_images)

@router.delete("/{product_id}", status_code=204)
def delete_product(
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    product: Product = Depends(validate_product_owner)
) -> None:
    productService.delete_product(db, product)
    return None

@router.post("/{product_id}/image", status_code=200)
def upload_product_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    product: Product = Depends(validate_product_owner)
) -> ProductImage:
    return productService.upload_product_image(
        db=db,
        product_id=product.id, 
        image=image,
        background_tasks=background_tasks
    )

@router.delete("/{product_id}/image/{image_id}", status_code=204)
def delete_product_image(
    db: Session = Depends(get_db_session),
    productService: ProductService = Depends(),
    product_image: ProductImage = Depends(validate_product_image_owner)
) -> None:
    productService.delete_product_image(db, product_image)
    return None

# ✅ 상품 구매 기능 추가
@router.post("/{product_id}/purchase", status_code=201)
def purchase_product(
    product_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """ 상품을 구매하는 기능 """
    
    # 1️⃣ 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2️⃣ 본인이 올린 상품인지 확인 (자기 자신은 구매할 수 없음)
    if product.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot purchase your own product")

    # 3️⃣ 이미 구매한 기록이 있는지 확인
    existing_purchase = db.exec(
        select(Purchase).where(Purchase.user_id == current_user.id, Purchase.product_id == product_id)
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="You have already purchased this product")

    # 4️⃣ 구매 등록
    new_purchase = Purchase(
        user_id=current_user.id,
        product_id=product_id,
        purchase_date=datetime.now()
    )
    db.add(new_purchase)

    # 5️⃣ 상품 상태를 `soldout = True` 로 변경
    product.soldout = True

    db.commit()
    db.refresh(new_purchase)

    return {"message": "Purchase successful", "purchase_id": new_purchase.id, "buyer_id": new_purchase.user_id}

# ✅ 내가 구매한 상품 목록 조회
@router.get("/purchases/me", status_code=200)
def get_my_purchases(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> list[ProductResponse]:
    """ 현재 로그인한 사용자의 구매 목록 조회 """
    
    # 1️⃣ 현재 사용자가 구매한 상품 조회
    purchases = db.exec(
        select(Purchase).where(Purchase.user_id == current_user.id)
    ).all()

    if not purchases:
        return []

    # 2️⃣ 구매한 상품 정보 가져오기
    productService = ProductService()
    purchased_products = [
        productService.get_product(db, purchase.product_id) for purchase in purchases
    ]
    
    return [
        ProductResponse(product=product, productImages=productService.get_product_images(db, product.id))
        for product in purchased_products
    ]

# ✅ 특정 상품의 구매 정보 조회
@router.get("/{product_id}/purchase", status_code=200)
def get_product_purchase_info(
    product_id: int,
    db: Session = Depends(get_db_session)
) -> dict:
    """ 특정 상품이 구매되었는지 확인 """
    
    # 1️⃣ 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2️⃣ 상품이 구매되었는지 확인
    purchase = db.exec(
        select(Purchase).where(Purchase.product_id == product_id)
    ).first()

    if not purchase:
        return {"purchased": False}

    return {
        "purchased": True,
        "buyer_id": purchase.user_id,
        "purchase_date": purchase.purchase_date
    }