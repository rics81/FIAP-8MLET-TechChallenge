from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from scripts.database import get_db
from scripts import crud, schemas
from scripts.models import Book, Category

router = APIRouter()

@router.get("/", response_model=List[schemas.Book])
def get_all_books(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return (1-1000)"),
    db: Session = Depends(get_db)
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
def get_book_by_upc(
    upc: str,
    db: Session = Depends(get_db)
):
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
    title: Optional[str] = Query(None, description="Search in book titles (case-insensitive, partial match)"),
    category: Optional[str] = Query(None, description="Search in category names (case-insensitive, partial match)"),
    db: Session = Depends(get_db)
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