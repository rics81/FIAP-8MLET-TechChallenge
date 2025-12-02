from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    upc: str
    title: str
    price: float
    rating: str
    availability: str
    image_url: Optional[str]

class BookCreate(BookBase):
    category_id: int

class Book(BookBase):
    id: int
    category_id: int
    category: Category
    class Config:
        from_attributes = True

class StatsOverview(BaseModel):
    total_books: int
    average_price: float
    rating_distribution: dict

class CategoryStats(BaseModel):
    category: str
    book_count: int
    average_price: float