# app/api/endpoints/books_advanced.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/top-rated", response_model=list[schemas.Book])
def get_top_rated_books(limit: int = 10, db: Session = Depends(get_db)):
    """Get top rated books (rating 5)"""
    books = db.query(models.Book).filter(
        models.Book.rating == "Five"
    ).limit(limit).all()
    return books

@router.get("/price-range", response_model=list[schemas.Book])
def get_books_by_price_range(
    min_price: float = Query(0.0, ge=0),
    max_price: float = Query(100.0, ge=0),
    db: Session = Depends(get_db)
):
    """Get books within a specific price range"""
    books = db.query(models.Book).filter(
        models.Book.price >= min_price,
        models.Book.price <= max_price
    ).all()
    return books