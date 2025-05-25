from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from search_api import app as search_app

app = FastAPI(title="Koala Search - Full Stack", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api", search_app)

if os.path.exists("frontend"):
    app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
    app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
    
    if not os.path.exists("frontend/assets"):
        os.makedirs("frontend/assets")
    app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
    
    @app.get("/sw.js")
    async def serve_sw():
        if os.path.exists("frontend/sw.js"):
            return FileResponse("frontend/sw.js")
        return {"error": "Service worker not found"}
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse("frontend/index.html")
    
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        if path.startswith("api/"):
            return {"error": "API route not found"}
        
        file_path = f"frontend/{path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse("frontend/index.html")

else:
    @app.get("/")
    async def no_frontend():
        return {"error": "Frontend directory not found"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Koala Search...")
    print("Frontend: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080) 