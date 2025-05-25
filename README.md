# 🐨 Koala

A web search engine built with FastAPI. Koala allows you to crawl websites, index their content, and perform semantic search with relevance scoring.

## Features

- **Semantic Search**: Advanced search using sentence transformers for better relevance
- **Web Crawling**: Automated website crawling with configurable depth and page limits
- **Real-time Analytics**: Search statistics and popular query tracking
- **RESTful API**: Full-featured API for integration with other applications
- **Background Processing**: Non-blocking website crawling with job status tracking

## Quick Start

### Prerequisites

- Python 3.10 or higher
- UV (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Abhinavexists/Koala.git
   cd koala
   ```

2. Install backend dependencies:

   ```
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Recommended**: Install with `uv` (faster, more reliable):

   ```
   cd backend
   uv venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .

4. **Start the server**

   ```bash
   python static_server.py
   ```

5. **Start the search api**

   ```bash
   python search_api.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:8000`

## Usage Guide

### Adding Websites

1. Go to the **Websites** tab
2. Fill in the website details:
   - **URL**: The website to crawl (e.g., `https://example.com`)
   - **Name**: Display name for the website
   - **Description**: Optional description
   - **Max Pages**: Maximum number of pages to crawl (default: 50)
   - **Max Depth**: How deep to crawl from the starting URL (default: 2)
3. Click **Add Website**
4. The system will start crawling in the background

### Searching

1. Go to the **Search** tab
2. Enter your search query in the search box
3. Press Enter or click the Search button
4. View results with relevance scores and snippets
5. Use pagination to browse through results

### Analytics

1. Go to the **Analytics** tab to view:
   - Total number of searches performed
   - Number of websites indexed
   - Active crawling jobs
   - Popular search queries

### Key Endpoints

- `GET /api/search` - Perform search queries
- `GET /api/websites` - List all websites
- `POST /api/websites` - Add new website to crawl
- `DELETE /api/websites/{id}` - Remove website
- `POST /api/websites/{id}/recrawl` - Recrawl website
- `GET /api/popular` - Get popular search queries
- `GET /api/stats` - Get system statistics

### Example API Usage

```bash
# Search for content
curl "http://localhost:8080/api/search?q=python&page=1&per_page=10"

# Add a website
curl -X POST "http://localhost:8080/api/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Site",
    "max_pages": 100,
    "max_depth": 3
  }'
```

## Architecture

### Backend (Python/FastAPI)

- **search_api.py**: Main API endpoints and business logic
- **search_engine.py**: Semantic search implementation using sentence transformers
- **crawler.py**: Web crawling functionality with BeautifulSoup
- **static_server.py**: Combined static file server and API gateway

### Data Storage

- **prepared_data.json**: Indexed website content and metadata
- **websites.json**: Website configuration and crawl status
- **Vector Index**: In-memory semantic search index using FAISS

## Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)

### Search Configuration

- **Model**: Uses `all-MiniLM-L6-v2` sentence transformer model
- **Device**: Automatically detects CUDA/CPU
- **Index Type**: FAISS for efficient similarity search

## Project Structure

```
koala/
├── frontend/           # Frontend assets
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript modules
│   └── index.html     # Main HTML file
├── search_api.py      # API endpoints
├── search_engine.py   # Search implementation
├── crawler.py         # Web crawler
├── static_server.py   # Server entry point
├── pyproject.toml     # project info
└── requirements.txt   # Python dependencies
```

### Running in Development Mode

1. **Backend only** (API on port 8000):

   ```bash
   python search_api.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

(Just a fun practice project to gain an understanding of Redis, crawlers, and semantic search)
