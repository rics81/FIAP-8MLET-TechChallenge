from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from scripts.database import get_db
from scripts import schemas
from scripts.auth import get_current_user
import subprocess
import sys
import threading
from typing import Dict, Any

router = APIRouter()

# Store scraping job status
scraping_jobs: Dict[str, Dict[str, Any]] = {}

def run_scraper_async(job_id: str):
    """Run scraper in a separate thread"""
    try:
        from scripts.scraper import scrape_books
        scrape_books()
        scraping_jobs[job_id]["status"] = "completed"
        scraping_jobs[job_id]["output"] = "Scraping completed successfully"
    except Exception as e:
        scraping_jobs[job_id]["status"] = "failed"
        scraping_jobs[job_id]["error"] = str(e)

@router.post("/trigger/", response_model=schemas.ScrapingResponse)
async def trigger_scraping(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger the scraping process (requires authentication)
    
    This endpoint starts the scraping process in the background.
    Only authenticated users can trigger this operation.
    """
    import uuid
    from datetime import datetime
    
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    scraping_jobs[job_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "output": "",
        "error": "",
        "books_added": 0,
        "books_skipped": 0
    }
    
    # Run scraper in background
    background_tasks.add_task(run_scraper_async, job_id)
    
    return {
        "status": "started",
        "message": f"Scraping job started with ID: {job_id}",
        "job_id": job_id
    }

@router.get("/status/{job_id}")
async def get_scraping_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status of a scraping job (requires authentication)
    """
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = scraping_jobs[job_id]
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "started_at": job.get("started_at"),
        "books_added": job.get("books_added", 0),
        "books_skipped": job.get("books_skipped", 0),
        "has_output": bool(job.get("output")),
        "has_error": bool(job.get("error"))
    }

@router.get("/status/{job_id}/output")
async def get_scraping_output(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the full output of a completed scraping job (requires authentication)
    """
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = scraping_jobs[job_id]
    
    if job["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Job is still running")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "output": job.get("output", ""),
        "error": job.get("error", "")
    }