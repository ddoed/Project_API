from app.models.models import Product, ProductImage
from app.models.product_model import ProductRequest, ProductResponse, ProductSortType
from app.dependencies import save_UploadFile, delete_file
from fastapi import UploadFile, File, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timezone

class ProductService:
    def get_product(self, db: Session,
                    product_id: int) -> Product:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        return product
    
    def get_products(self, db: Session,
                          q: Optional[str] = None,
                          category_id: Optional[int] = None,
                          soldout: Optional[bool] = None,
                          min_price: Optional[int] = None,
                          max_price: Optional[int] = None,
                          sort_type: Optional[ProductSortType] = ProductSortType.ACCURACY,
                          page: int = 0,
                          limit: int = 10) -> list[Product]:
        query = select(Product)
        if q:
            query = query.where(Product.title.contains(q) | Product.content.contains(q))
        if category_id:
            query = query.where(Product.category_id == category_id)
        if soldout is not None:
            query = query.where(Product.soldout == soldout)
        if min_price:
            query = query.where(Product.price >= min_price)
        if max_price:
            query = query.where(Product.price <= max_price)
        if sort_type == ProductSortType.LATEST:
            query = query.order_by(Product.date)
        else:
            # ProductSortType.ACCURACY
            # 당근에서는 정확도 순이라고 적혀있는데, 구현은 좀 더 생각해봐야할 듯듯
            query = query.order_by(Product.heart_count)
        query = query.offset(page * limit).limit(limit)

        products = db.exec(query.offset(page * limit).limit(limit)).all()
        return products
    
    def create_product(self, db: Session,
                             productRequest: ProductRequest
    ) -> Product:
        product = Product(
            title=productRequest.title,
            content=productRequest.content,
            price=productRequest.price,
            date=datetime.now(tz=timezone.utc), # ?: UTC Time을 사용할 것인가?
            user_id=productRequest.user_id,
            category_id=productRequest.category_id,
            soldout=False,
            heart_count=0
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update_product(self, db: Session,
                             product_id: int,
                             productRequest: ProductRequest) -> Product:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        if product.user_id != productRequest.user_id:
            raise HTTPException(status_code=403, detail="User does not have permission.")
        product.sqlmodel_update(productRequest.model_dump())
        db.commit()
        db.refresh(product)
        return product
    
    def delete_product(self, db: Session, product_id: int) -> None:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        db.delete(product)
        db.commit()
        return None
    
    def get_product_images(self, db: Session, 
                                 product_id: int) -> list[ProductImage]:
        return db.exec(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
        ).all()
    
    async def upload_product_image(self, db: Session,
                             product_id: int,
                             image: UploadFile) -> ProductImage:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        file_path = await save_UploadFile(image, f"{product.id}_{image.filename}")
        if not file_path:
            raise HTTPException(status_code=400, detail="File already exists.")
        productImage = ProductImage(product_id=product.id, image_URI=file_path)
        db.add(productImage)
        db.commit()
        db.refresh(productImage)
        return productImage
    
    def delete_product_image(self, db: Session,
                             product_id: int,
                             image_id: int) -> None:
        productImage = db.exec(
            select(ProductImage).where(
                ProductImage.product_id == product_id, 
                ProductImage.id == image_id
            )
        ).first()
        if not productImage:
            raise HTTPException(status_code=404, detail="ProductImage not found.")
        db.delete(productImage)
        delete_file(productImage.image_URI)
        db.commit()
        return True
    
    def delete_all_product_images(self, db: Session,
                                  product_id: int) -> None:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        for productImage in self.get_product_images(db, product_id):
            db.delete(productImage)
        db.commit()
        return None