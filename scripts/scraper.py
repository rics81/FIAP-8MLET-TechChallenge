import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from urllib.parse import urljoin
import time
import re

from scripts.database import SessionLocal, init_db
from scripts.models import Book, Category

HOME_URL = "https://books.toscrape.com/"
DELAY = 1  # Delay between requests to be polite

def get_or_create_category(db: Session, name: str) -> Category:
    """Return existing category or create a new one."""
    category = db.query(Category).filter_by(name=name).first()
    if not category:
        category = Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
    return category

def scrape_book_detail(book_url: str):
    """Scrape details from a book's individual page."""
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract UPC from the product information table
        upc_element = soup.find("th", string="UPC")
        upc = upc_element.find_next_sibling("td").text if upc_element else None
        
        # Extract other details from the detail page
        title = soup.find("h1").text if soup.find("h1") else None
        
        # Price (get from product_main section)
        price_element = soup.select_one("p.price_color")
        price_text = price_element.text if price_element else "£0.00"
        price = float(re.sub(r'[^\d.]', '', price_text))
        
        # Rating
        rating_element = soup.select_one("p.star-rating")
        rating = rating_element["class"][1] if rating_element else "Zero"
        
        # Availability
        availability_element = soup.select_one("p.instock.availability")
        availability = availability_element.text.strip() if availability_element else "Unknown"
        
        # Image URL
        image_element = soup.select_one("#product_gallery img")
        image_url = urljoin(book_url, image_element["src"]) if image_element else None
        
        return {
            "upc": upc,
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error scraping book detail page {book_url}: {e}")
        return None

def get_category_links():
    """Scrape homepage to collect all category links."""
    response = requests.get(HOME_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    
    # Skip the first link which is usually "All categories"
    for a in soup.select("div.side_categories ul li a")[1:]:
        href = a["href"].strip()
        full_url = urljoin(HOME_URL, href)
        category_name = a.text.strip()
        links.append((category_name, full_url))
    
    return links

def book_exists(db: Session, upc: str) -> bool:
    """Check if a book already exists in the database by UPC."""
    return db.query(Book).filter(Book.upc == upc).first() is not None

def scrape_category(db: Session, category_name: str, category_url: str):
    """Scrape all pages of a category, avoiding duplicates."""
    category = get_or_create_category(db, category_name)
    page_url = category_url
    books_added = 0
    books_skipped = 0

    while True:
        print(f"Scraping page: {page_url}")
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        books = soup.select("article.product_pod")
        print(f"Found {len(books)} books on this page")
        
        for article in books:
            # Get the book detail page URL
            book_relative_url = article.h3.a["href"]
            
            # Convert to absolute URL
            book_url = get_book_url(book_relative_url)
            print(f"Fetching: {book_url}")
            
            # Scrape book details
            book_details = scrape_book_detail(book_url)
            
            if not book_details or not book_details["upc"]:
                print(f"Skipping book without UPC: {book_url}")
                books_skipped += 1
                continue
            
            # Check if book already exists
            if book_exists(db, book_details["upc"]):
                print(f"Book with UPC {book_details['upc']} already exists. Skipping.")
                books_skipped += 1
                continue
            
            # Create and add new book
            book = Book(
                upc=book_details["upc"],
                title=book_details["title"],
                price=book_details["price"],
                rating=book_details["rating"],
                availability=book_details["availability"],
                image_url=book_details["image_url"],
                category=category,
            )
            
            db.add(book)
            books_added += 1
            print(f"Added book: {book_details['title']} (UPC: {book_details['upc']})")
        
        # Commit after each page
        db.commit()
        print(f"Page complete. Added: {books_added}, Skipped: {books_skipped}")
        
        # Be polite - delay between pages
        time.sleep(DELAY)
        
        # Check for next page
        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_href = next_btn["href"]
            page_url = urljoin(page_url, next_href)
        else:
            break
    
    return books_added, books_skipped

def get_book_url(book_relative_url: str) -> str:
    """
    Convert a book relative URL to a full absolute URL.
    
    Examples:
    - ../../../its-only-the-himalayas_981/index.html 
      -> https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
    - catalogue/its-only-the-himalayas_981/index.html
      -> https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
    """
    # Remove any leading ../../../ patterns
    if book_relative_url.startswith("../../../"):
        book_relative_url = book_relative_url[9:]  # Remove "../../../"
    
    # Ensure it starts with catalogue/
    if not book_relative_url.startswith("catalogue/"):
        book_relative_url = "catalogue/" + book_relative_url
    
    # Join with HOME_URL
    return urljoin(HOME_URL, book_relative_url)

def scrape_books():
    """Main function to scrape all books."""
    init_db()  # ensure tables exist (will update schema if needed)
    db = SessionLocal()
    
    try:
        category_links = get_category_links()
        total_added = 0
        total_skipped = 0
        
        for category_name, category_url in category_links:
            print(f"\n{'='*50}")
            print(f"Scraping category: {category_name}")
            print(f"URL: {category_url}")
            print(f"{'='*50}")
            
            added, skipped = scrape_category(db, category_name, category_url)
            total_added += added
            total_skipped += skipped
            
            # Delay between categories
            time.sleep(DELAY * 2)
        
        print(f"\n{'='*50}")
        print(f"SCRAPING COMPLETE")
        print(f"Total books added: {total_added}")
        print(f"Total books skipped (duplicates): {total_skipped}")
        print(f"Total processed: {total_added + total_skipped}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    scrape_books()