from sqlalchemy.orm import Session
from sqlalchemy import func
from scripts import models, schemas

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books_by_title_and_category(db: Session, title: str = None, category: str = None):
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if category:
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category}%"))
    return query.all()

def get_books_by_title_and_category(db: Session, title: str = None, category: str = None):
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if category:
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category}%"))
    return query.all()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_stats_overview(db: Session):
    total_books = db.query(func.count(models.Book.id)).scalar()
    average_price = db.query(func.avg(models.Book.price)).scalar()
    rating_distribution = db.query(
        models.Book.rating, 
        func.count(models.Book.id)
    ).group_by(models.Book.rating).all()
    
    return {
        "total_books": total_books,
        "average_price": round(average_price, 2) if average_price else 0,
        "rating_distribution": dict(rating_distribution)
    }

def get_stats_by_categories(db: Session):
    categories_stats = db.query(
        models.Category.name,
        func.count(models.Book.id),
        func.avg(models.Book.price)
    ).join(models.Book).group_by(models.Category.id, models.Category.name).all()
    
    return [
        {
            "category": category_name,
            "book_count": book_count,
            "average_price": round(avg_price, 2) if avg_price else 0
        }
        for category_name, book_count, avg_price in categories_stats
    ]