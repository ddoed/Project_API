from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import *
# * back_populates로 양방향 관계 설정

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(unique=True)
    password: str
    username: str
    role: str

    products: List["Product"] = Relationship(back_populates="user")
    likes: List["Likes"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    # * id 자동생성, 증가하는 숫자
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    # * id 자동생성, 증가하는 숫자
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
    images: List["ProductImage"] = Relationship(back_populates="product")
    likes: List["Likes"] = Relationship(back_populates="product")
    comments: List["Comment"] = Relationship(back_populates="product")

class ProductImage(SQLModel, table=True):
    # * 하나의 게시물에 여러개의 사진이 연결될 수 있도록 id를 설정
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