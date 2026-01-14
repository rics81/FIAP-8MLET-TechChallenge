from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from scripts.database import get_db

router = APIRouter()


@router.get("/")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Returns:
        dict: Health status and database connection status
    """
    try:
        # Wrap SQL query in text() function for SQLAlchemy 2.0 compatibility
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
