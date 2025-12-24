from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Request schemas
class ProductCreate(BaseModel):
    name: str = "Sample name"
    price: float = 0
    image: str = "/images/sample.jpg"
    brand: str = "Sample brand"
    category: str = "Sample category"
    count_in_stock: int = Field(0, alias="countInStock")
    description: str = "Sample description"

    class Config:
        populate_by_name = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    count_in_stock: Optional[int] = Field(None, alias="countInStock")

    class Config:
        populate_by_name = True


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str


# Response schemas
class ReviewResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    rating: int
    comment: str
    user: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ProductResponse(BaseModel):
    id: str = Field(alias="_id")
    user: str
    name: str
    image: str
    brand: str
    category: str
    description: str
    rating: float
    num_reviews: int = Field(alias="numReviews")
    price: float
    count_in_stock: int = Field(alias="countInStock")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    page: int
    pages: int
