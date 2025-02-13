# app/models/user_and_product_models.py
from pydantic import BaseModel, Field
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from pydantic import BaseModel
from datetime import *

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    login_id: str = Field(index=True)
    email: str = Field(unique=True)
    password: str = Field(default=None, exclude=True)
    username: str 
    role: str = Field(default="user")
    products: List["Product"] = Relationship(back_populates="user")
    likes: List["Likes"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")
    access_token: str | None = None
    created_at: int | None = Field(index=True) 
    purchases: List["Purchase"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    # id 자동생성, 증가하는 숫자
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    # id 자동생성, 증가하는 숫자
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    price: int
    # 판매 게시글을 올린 시각
    date: datetime
    heart_count: int = Field(default=0)
    # 판매자 id
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    soldout: bool = False

    user: User = Relationship(back_populates="products")
    category: Category = Relationship(back_populates="products")
    images: List["ProductImage"] = Relationship(back_populates="product", cascade_delete=True)
    likes: List["Likes"] = Relationship(back_populates="product", cascade_delete=True)
    comments: List["Comment"] = Relationship(back_populates="product", cascade_delete=True)
    purchases: List["Purchase"] = Relationship(back_populates="product", cascade_delete=True)


class ProductImage(SQLModel, table=True):
    # 하나의 게시물에 여러개의 사진이 연결될 수 있도록 id를 설정
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    image_URI: str

    product: Product = Relationship(back_populates="images")

class Likes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    user_id: int = Field(foreign_key="user.id")

    product: Product = Relationship(back_populates="likes")
    user: User = Relationship(back_populates="likes")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    user_id: int = Field(foreign_key="user.id")
    content: str
    last_modified: datetime = Field(default_factory=datetime.now)

    product: Product = Relationship(back_populates="comments")
    user: User = Relationship(back_populates="comments")

class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # 구매자 id
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    # 판매 완료 시각
    purchase_date: datetime
    
    user: User = Relationship(back_populates="purchases")
    product: Product = Relationship(back_populates="purchases")

class ProductRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)
    price: int = Field(..., ge=0)
    category_id: int = Field(..., ge=0) # TODO: validate category_id

class ProductResponse(BaseModel):
    product: Product
    productImages: list[ProductImage]

class ProductSortType(Enum):
    ACCURACY = "accuracy"
    LATEST = "latest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    LIKES = "likes"


class RespComments(BaseModel):
    comments : list[Comment]