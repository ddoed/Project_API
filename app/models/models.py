from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    # unique id입력 필요
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(unique=True)
    password: str
    username: str
    role: str

    # back_populates로 양방향 연결
    products: List["Product"] = Relationship(back_populates="user")
    likes: List["Likes"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    # id값 미 입력시 자동 증가
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    price: int
    heart_count: int = Field(default=0)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    user: User = Relationship(back_populates="products")
    category: Category = Relationship(back_populates="products")
    images: List["ProductImage"] = Relationship(back_populates="product")
    likes: List["Likes"] = Relationship(back_populates="product")
    comments: List["Comment"] = Relationship(back_populates="product")

class ProductImage(SQLModel, table=True):
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
