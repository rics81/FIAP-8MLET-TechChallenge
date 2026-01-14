from fastapi import FastAPI
from api.routes import auth, books, categories, health, scraper_router, stats
from scripts.database import init_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Book API",
    description="A public API for querying books data from books.toscrape.com",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authentication endpoints (login, refresh tokens)",
        },
        {"name": "books", "description": "Operations with books"},
        {"name": "categories", "description": "Operations with book categories"},
        {"name": "health", "description": "Health check endpoints"},
        {"name": "stats", "description": "Statistics endpoints"},
        {
            "name": "scraping",
            "description": "Scraping operations (requires authentication)",
        },
    ],
)


# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(scraper_router.router, prefix="/api/v1/scraping", tags=["scraping"])


@app.get("/")
def root():
    return {
        "message": "Book API - Check /docs for API documentation",
        "login": "/api/v1/login",
        "docs": "/docs",
        "redoc": "/redoc",
    }
