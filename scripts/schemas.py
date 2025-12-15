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
    rating: int
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

# Authentication schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ScrapingResponse(BaseModel):
    status: str
    message: str
    books_added: Optional[int] = None
    books_skipped: Optional[int] = None