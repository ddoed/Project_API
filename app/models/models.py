from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
<<<<<<< HEAD
from datetime import *
# * back_populates로 양방향 관계 설정

class User(SQLModel, table=True):
=======

class User(SQLModel, table=True):
    # unique id입력 필요
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(unique=True)
    password: str
    username: str
    role: str

<<<<<<< HEAD
=======
    # back_populates로 양방향 연결
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
    products: List["Product"] = Relationship(back_populates="user")
    likes: List["Likes"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
<<<<<<< HEAD
    # * id 자동생성, 증가하는 숫자
=======
    # id값 미 입력시 자동 증가
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
<<<<<<< HEAD
    # * id 자동생성, 증가하는 숫자
=======
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    price: int
<<<<<<< HEAD
    date: datetime
=======
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
    heart_count: int = Field(default=0)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    user: User = Relationship(back_populates="products")
    category: Category = Relationship(back_populates="products")
    images: List["ProductImage"] = Relationship(back_populates="product")
    likes: List["Likes"] = Relationship(back_populates="product")
    comments: List["Comment"] = Relationship(back_populates="product")

class ProductImage(SQLModel, table=True):
<<<<<<< HEAD
    # * 하나의 게시물에 여러개의 사진이 연결될 수 있도록 id를 설정
=======
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
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
<<<<<<< HEAD

class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    purchase_date: datetime
    
    user: User = Relationship(back_populates="purchases")
    product: Product = Relationship(back_populates="purchases")
=======
>>>>>>> a80b2eeb35178a50597822458b7042e39da644f8
