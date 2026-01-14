from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from scripts.database import get_db
from scripts import crud, schemas
from scripts.models import Book

router = APIRouter()


@router.get("/", response_model=List[schemas.Book])
def get_all_books(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return (1-1000)"
    ),
    db: Session = Depends(get_db),
):
    """
    Get ALL books from the database.

    Returns all books stored in the books table with optional pagination.

    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (default: 100, max: 1000)

    Example:
    - GET /api/v1/books?skip=0&limit=20
    """
    books = crud.get_books(db, skip=skip, limit=limit)
    return books


@router.get("/{upc}", response_model=schemas.Book)
def get_book_by_upc(upc: str, db: Session = Depends(get_db)):
    """
    Get a single book by its UPC code.

    Parameters:
    - upc: The Universal Product Code (UPC) of the book

    Example:
    - GET /api/v1/books/a897fe39b1053632
    """
    # Search for book by UPC instead of ID
    book = crud.get_book(db, upc=upc)

    if not book:
        raise HTTPException(status_code=404, detail=f"Book with UPC '{upc}' not found")

    return book


@router.get("/search/", response_model=List[schemas.Book])
def search_books(
    title: Optional[str] = Query(
        None, description="Search in book titles (case-insensitive, partial match)"
    ),
    category: Optional[str] = Query(
        None, description="Search in category names (case-insensitive, partial match)"
    ),
    db: Session = Depends(get_db),
):
    """
    Search books by title and/or category.

    Parameters:
    - title: Optional - Search text to match in book titles
    - category: Optional - Category name to filter books

    Search is case-insensitive and supports partial matching.

    Examples:
    - GET /api/v1/books/search?title=python
    - GET /api/v1/books/search?category=fiction
    - GET /api/v1/books/search?title=python&category=programming
    """
    books = crud.get_books_by_title_and_category(db, title=title, category=category)
    return books


@router.get("/top-rated/", response_model=List[schemas.Book])
def get_top_rated_books(
    min_rating: int = Query(
        4, ge=0, le=5, description="Minimum rating to filter top-rated books"
    ),
    db: Session = Depends(get_db),
):
    """
    Get books with ratings above a specified threshold.

    Parameters:
    - min_rating: Minimum rating to filter books (default: 4)

    Example:
    - GET /api/v1/books/top-rated?min_rating=3
    """
    books = (
        db.query(Book)
        .filter(Book.rating >= min_rating)
        .order_by(Book.rating.desc())
        .all()
    )
    return books


@router.get("/price-range/", response_model=List[schemas.Book])
def get_books_in_price_range(
    min_price: float = Query(0.0, ge=0.0, description="Minimum price to filter books"),
    max_price: float = Query(
        1000.0, ge=0.0, description="Maximum price to filter books"
    ),
    db: Session = Depends(get_db),
):
    """
    Get books within a specified price range.

    Parameters:
    - min_price: Minimum price to filter books (default: 0.0)
    - max_price: Maximum price to filter books (default: 1000.0)

    Example:
    - GET /api/v1/books/price-range?min_price=10.0&max_price=50.0
    """
    books = (
        db.query(Book)
        .filter(Book.price >= min_price, Book.price <= max_price)
        .order_by(Book.price)
        .all()
    )
    return books
