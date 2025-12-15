# app/api/endpoints/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from scripts.database import get_db
from scripts import crud, schemas

router = APIRouter()

@router.get("/overview/", response_model=schemas.StatsOverview)
def get_stats_overview(db: Session = Depends(get_db)):
    """Get overview statistics of the book collection"""
    stats = crud.get_stats_overview(db)
    return stats

@router.get("/categories/", response_model=list[schemas.CategoryStats])
def get_stats_by_categories(db: Session = Depends(get_db)):
    """Get statistics by categories"""
    stats = crud.get_stats_by_categories(db)
    return stats