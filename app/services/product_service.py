# app/services/product_service.py
from app.models.user_and_product_model import *
from app.io import create_file_name, save_file, delete_file
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy import or_
from sqlalchemy.sql.expression import desc
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timezone

class ProductService:
    def get_product(self, db: Session,product_id: int) -> Product:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
    
    def get_products(
        self, 
        db: Session,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
        soldout: Optional[bool] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        sort_type: Optional[ProductSortType] = ProductSortType.ACCURACY,
        page: int = 0,
        limit: int = 10
    ) -> list[Product]:
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
        if sort_type == ProductSortType.ACCURACY:
            pass
        elif sort_type == ProductSortType.LATEST:
            query = query.order_by(Product.date.desc())
        elif sort_type == ProductSortType.PRICE_ASC:
            query = query.order_by(Product.price)
        elif sort_type == ProductSortType.PRICE_DESC:
            query = query.order_by(Product.price.desc())
        elif sort_type == ProductSortType.LIKES:
            query = query.order_by(Product.heart_count.desc())
        query = query.offset(page * limit).limit(limit)

        products = db.exec(
            query.offset(page * limit)
                 .limit(limit)
        ).all()
        return products
    
    def create_product(self, db: Session, productRequest: ProductRequest, user: User) -> Product:
        product = Product(
            title=productRequest.title,
            content=productRequest.content,
            price=productRequest.price,
            date=datetime.now(tz=timezone.utc),
            user_id=user.id,
            category_id=productRequest.category_id,
            soldout=False,
            heart_count=0
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update_product(self, db: Session, productRequest: ProductRequest, product: Product) -> Product:
        product.sqlmodel_update(productRequest.model_dump(exclude_unset=True))
        product.date = datetime.now(tz=timezone.utc)
        db.commit()
        db.refresh(product)
        return product
    
    def delete_product(self, db: Session, product: Product) -> None:
        
        self.delete_all_product_images(db, product.id)
        db.delete(product)
        db.commit()
        return None
    
    def validate_image(self, image: UploadFile) -> tuple[str, bytes]:
        file_name = create_file_name(image.filename)
        file_content = image.file.read()
        if not file_name:
            raise HTTPException(status_code=400, detail="File type not allowed.")
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file.")
        
        return file_name, file_content

    def upload_product_image(
        self, db: Session, product_id: int, image: UploadFile, background_tasks: BackgroundTasks,
    ) -> ProductImage:
        file_name, file_content = self.validate_image(image)

        background_tasks.add_task(save_file, file_name, file_content)

        productImage = ProductImage(product_id=product_id, image_URI=file_name)
        db.add(productImage)
        db.commit()
        db.refresh(productImage)

        return productImage
    
    def get_product_image(self, db: Session, product_id: int, image_id: int) -> ProductImage:
        product_image = db.exec(
            select(ProductImage).where(
                ProductImage.product_id == product_id, 
                ProductImage.id == image_id
            )
        ).first()
        if not product_image:
            raise HTTPException(status_code=404, detail="ProductImage not found.")
        
        return product_image
    
    def get_product_images(self, db: Session, product_id: int) -> list[ProductImage]:
        product_images = db.exec(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
        ).all()

        return product_images
    
    def delete_product_image(self, db: Session, product_image: ProductImage) -> None:
        file_deleted = delete_file(product_image.image_URI)
        if not file_deleted:
            # raise HTTPException(status_code=500, detail="Failed to delete file.")
            print(f"Warning: Failed to delete file {product_image.image_URI}")
        db.delete(product_image)
        db.commit()
    
    def delete_all_product_images(self, db: Session, product_id: int) -> None:
        product_images = self.get_product_images(db, product_id)
        for product_image in product_images:
            file_deleted = delete_file(product_image.image_URI)
            if not file_deleted:
                # raise HTTPException(status_code=500, detail="Failed to delete file.")
                print(f"Warning: Failed to delete file {product_image.image_URI}")
            db.delete(product_image)
        db.commit()
        return None