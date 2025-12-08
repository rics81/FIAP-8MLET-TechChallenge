from fastapi import FastAPI
from api.routes import books, categories, health, stats
from scripts.database import init_db
import os

app = FastAPI(
    title="Book API",
    description="A public API for querying books data from books.toscrape.com",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include routers
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])

@app.get("/")
def root():
    return {"message": "Book API - Check /docs for API documentation"}