from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from scripts.database import get_db
from scripts import crud, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.Category])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all categories with pagination"""
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories