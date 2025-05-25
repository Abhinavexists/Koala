import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional

class SearchEngine:
    def __init__(self, data_path, cache_path='vector_index'):
        with open(data_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

        if isinstance(self.data[0], list):
            self.urls = [entry[0] for entry in self.data]
            self.texts = [entry[1] for entry in self.data]
            self.metadata = [{"title": "", "description": ""} for _ in self.data]
        else:
            self.urls = [entry.get("url", "") for entry in self.data]
            self.texts = [entry.get("content", "") for entry in self.data]
            self.metadata = [
                {
                    "title": entry.get("title", ""),
                    "description": entry.get("description", "")
                }
                for entry in self.data
            ]

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384
        
        self.index_path = f"{cache_path}.index"
        self.create_or_load_index()
    
    def create_or_load_index(self):
        if os.path.exists(self.index_path):
            print("[INFO] Loading cached vector index...")
            self.index = faiss.read_index(self.index_path)
        else:
            print("[INFO] Creating new vector index...")
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
            embeddings = self.model.encode(self.texts, show_progress_bar=True)
            embeddings = embeddings.astype('float32')
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            faiss.write_index(self.index, self.index_path)
    
    def search(self, query: str, top_k: int = 5, sort_by: str = 'score', 
               page: int = 1, per_page: int = 5, domain: Optional[str] = None) -> List[Tuple[str, float, str]]:
        query_vector = self.model.encode([query]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        k = min(len(self.texts), top_k * per_page * 2)
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.urls):
                url = self.urls[idx]
                score = float(distances[0][i])
                text = self.texts[idx]
                
                if domain and domain not in url:
                    continue
                    
                snippet = self.search_snippet(text, query)
                results.append((url, score, snippet))
        
        if sort_by == 'score':
            results.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == 'relevance':
            results.sort(key=lambda x: x[1], reverse=False)
            
        start = (page - 1) * per_page
        end = start + per_page
        
        return results[start:end]
    
    def search_snippet(self, text, query, window_size=50):
        query_lower = query.lower()
        text_lower = text.lower()
        
        index = text_lower.find(query_lower)
        if index == -1:
            return text[:2*window_size] + ("..." if len(text) > 2*window_size else "")
        
        start = max(index - window_size, 0)
        end = min(index + len(query) + window_size, len(text))
        
        snippet = text[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
            
        return snippet

if __name__ == "__main__":
    search_engine = SearchEngine('prepared_data.json')
    while True:
        query = input("Enter your search query: ")
        if query.lower() == "exit":
            break
        results = search_engine.search(query)
        for url, score, snippet in results:
            print(f"{url} - Score: {score:.4f}\nSnippet: {snippet}\n")
