from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import time
from search_engine import SearchEngine
from crawler import Crawler
import json
from datetime import datetime
import os
import uuid

app = FastAPI(title="Koala Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_engine = None
crawl_jobs = {}
websites_db = "websites.json"

def get_search_engine():
    global search_engine
    if search_engine is None and os.path.exists("prepared_data.json"):
        search_engine = SearchEngine("prepared_data.json")
    return search_engine

def load_websites():
    if os.path.exists(websites_db):
        with open(websites_db, 'r') as f:
            return json.load(f)
    return []

def save_websites(websites):
    with open(websites_db, 'w') as f:
        json.dump(websites, f, indent=2)

class SearchResult(BaseModel):
    url: str
    score: float
    snippet: str
    title: Optional[str] = None
    
class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    time_taken: float
    page: int
    per_page: int
    query: str

class Website(BaseModel):
    url: HttpUrl
    name: str
    description: Optional[str] = ""
    max_pages: int = 50
    max_depth: int = 2

class WebsiteResponse(BaseModel):
    id: str
    url: str
    name: str
    description: str
    max_pages: int
    max_depth: int
    status: str
    pages_crawled: int
    last_crawled: Optional[str] = None
    created_at: str

class CrawlJob(BaseModel):
    id: str
    website_id: str
    status: str
    pages_crawled: int
    total_pages: int
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

search_stats = {
    "total_searches": 0,
    "recent_searches": [],
    "popular_queries": {}
}

SYNONYMS = {
    "python": ["python", "py", "python3"],
    "javascript": ["javascript", "js", "ecmascript"],
    "database": ["database", "db", "data store"],
    "web": ["web", "website", "site"],
    "tutorial": ["tutorial", "guide", "howto", "how-to"]
}

def expand_query(query: str) -> str:
    words = query.lower().split()
    expanded = []
    
    for word in words:
        expanded.append(word)
        for term, synonyms in SYNONYMS.items():
            if word == term:
                expanded.extend([s for s in synonyms if s != word])
                
    return " ".join(expanded)

def log_search(query: str, results_count: int, time_taken: float):
    global search_stats
    
    search_stats["total_searches"] += 1
    search_log = {
        "query": query,
        "results": results_count,
        "time": time_taken,
        "timestamp": datetime.now().isoformat()
    }
    search_stats["recent_searches"].append(search_log)
    
    if len(search_stats["recent_searches"]) > 100:
        search_stats["recent_searches"] = search_stats["recent_searches"][-100:]
    
    query_lower = query.lower()
    search_stats["popular_queries"][query_lower] = search_stats["popular_queries"].get(query_lower, 0) + 1

async def crawl_website_background(website_id: str, website_data: dict):
    job_id = str(uuid.uuid4())
    
    crawl_jobs[job_id] = {
        "id": job_id,
        "website_id": website_id,
        "status": "running",
        "pages_crawled": 0,
        "total_pages": website_data["max_pages"],
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "error_message": None
    }
    
    try:
        crawler = Crawler()
        data = crawler.crawl(
            website_data["url"], 
            max_pages=website_data["max_pages"],
            max_depth=website_data["max_depth"]
        )
        
        existing_data = []
        if os.path.exists("prepared_data.json"):
            with open("prepared_data.json", 'r') as f:
                existing_data = json.load(f)
        
        existing_data = [item for item in existing_data 
                        if not (isinstance(item, dict) and item.get("url", "").startswith(website_data["url"]))]
        
        existing_data.extend(data)
        
        with open("prepared_data.json", 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        websites = load_websites()
        for website in websites:
            if website["id"] == website_id:
                website["status"] = "completed"
                website["pages_crawled"] = len(data)
                website["last_crawled"] = datetime.now().isoformat()
                break
        save_websites(websites)
        
        crawl_jobs[job_id]["status"] = "completed"
        crawl_jobs[job_id]["pages_crawled"] = len(data)
        crawl_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        global search_engine
        search_engine = None
        
    except Exception as e:
        crawl_jobs[job_id]["status"] = "failed"
        crawl_jobs[job_id]["error_message"] = str(e)
        crawl_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        websites = load_websites()
        for website in websites:
            if website["id"] == website_id:
                website["status"] = "failed"
                break
        save_websites(websites)

@app.get("/")
async def root():
    return {"message": "Koala Search API", "version": "1.0.0"}

@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Results per page"),
    sort_by: str = Query("score", description="Sort by score or relevance"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    expand: bool = Query(True, description="Use query expansion")
):
    start_time = time.time()
    
    engine = get_search_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Search engine not ready. Please add and crawl some websites first.")
    
    query = expand_query(q) if expand else q
    
    results = engine.search(
        query=query,
        top_k=per_page * 2,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        domain=domain
    )
    
    formatted_results = [
        SearchResult(url=url, score=score, snippet=snippet) 
        for url, score, snippet in results
    ]
    
    time_taken = time.time() - start_time
    
    response = SearchResponse(
        results=formatted_results,
        total=len(formatted_results),
        time_taken=time_taken,
        page=page,
        per_page=per_page,
        query=q
    )
    
    log_search(q, len(formatted_results), time_taken)
    return response

@app.get("/websites", response_model=List[WebsiteResponse])
async def get_websites():
    websites = load_websites()
    return websites

@app.post("/websites", response_model=WebsiteResponse)
async def add_website(website: Website, background_tasks: BackgroundTasks):
    websites = load_websites()
    
    for existing in websites:
        if existing["url"] == str(website.url):
            raise HTTPException(status_code=400, detail="Website already exists")
    
    website_id = str(uuid.uuid4())
    website_data = {
        "id": website_id,
        "url": str(website.url),
        "name": website.name,
        "description": website.description,
        "max_pages": website.max_pages,
        "max_depth": website.max_depth,
        "status": "pending",
        "pages_crawled": 0,
        "last_crawled": None,
        "created_at": datetime.now().isoformat()
    }
    
    websites.append(website_data)
    save_websites(websites)
    
    background_tasks.add_task(crawl_website_background, website_id, website_data)
    
    return WebsiteResponse(**website_data)

@app.delete("/websites/{website_id}")
async def delete_website(website_id: str):
    websites = load_websites()
    websites = [w for w in websites if w["id"] != website_id]
    save_websites(websites)
    return {"message": "Website deleted"}

@app.post("/websites/{website_id}/recrawl")
async def recrawl_website(website_id: str, background_tasks: BackgroundTasks):
    websites = load_websites()
    website = next((w for w in websites if w["id"] == website_id), None)
    
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    website["status"] = "pending"
    save_websites(websites)
    
    background_tasks.add_task(crawl_website_background, website_id, website)
    
    return {"message": "Recrawl started"}

@app.get("/crawl-jobs", response_model=List[CrawlJob])
async def get_crawl_jobs():
    return list(crawl_jobs.values())

@app.get("/popular", response_model=Dict[str, int])
async def popular_queries(limit: int = Query(10, ge=1, le=100)):
    sorted_queries = sorted(
        search_stats["popular_queries"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    return dict(sorted_queries[:limit])

@app.get("/stats")
async def get_stats():
    websites = load_websites()
    return {
        "total_searches": search_stats["total_searches"],
        "recent_searches_count": len(search_stats["recent_searches"]),
        "unique_queries": len(search_stats["popular_queries"]),
        "total_websites": len(websites),
        "active_crawls": len([j for j in crawl_jobs.values() if j["status"] == "running"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
