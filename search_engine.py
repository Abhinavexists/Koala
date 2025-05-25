import os
import json
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self, data_path, cache_path='embeddings.pkl'):
        with open(data_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

        self.urls = [entry[0] for entry in self.data]
        self.texts = [entry[1] for entry in self.data]

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache_path = cache_path

        if os.path.exists(self.cache_path):
            print("[INFO] Loading cached embeddings...")
            with open(cache_path, 'rb') as file:
                self.embeddings = pickle.load(file)
        else:
            print("[INFO] Encoding texts...")
            self.embeddings = self.model.encode(self.texts, show_progress_bar=True)
            with open(self.cache_path, 'wb') as file:
                pickle.dump(self.embeddings, file)

    def search(self, query, top_k=5, sort_by='score', page=1, per_page=5, domain=None):
        query_vector = self.model.encode(query)
        scores = cosine_similarity([query_vector], self.embeddings).flatten()

        ranked_list = list(zip(self.urls, scores, self.texts))

        if domain:
            ranked_list = [item for item in ranked_list if domain in item[0]]

        if sort_by == 'score':
            ranked_list.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == 'relevance':
            ranked_list.sort(key=lambda x: x[1], reverse=False)

        # pagination
        start = (page - 1) * per_page
        end = start + per_page

        results = []
        for url, score, text in ranked_list[start:end]:
            snippet = self.search_snippet(text, query)
            results.append((url, score, snippet))
        return results
    
    def search_snippet(self, text, query, window_size=30):
        index = text.lower().find(query.lower())
        if index == -1:
            return text[:2*window_size] + "..."
        start = max(index - window_size, 0)
        end = min(index + len(query) + window_size, len(text))
        return "..." + text[start:end] + "..."
    
if __name__ == "__main__":
    search_engine = SearchEngine('prepared_data.json')
    while True:
        query = input("Enter your search query: ")
        if query.lower() == "exit":
            break
        results = search_engine.search(query)
        for url, score, snippet in results:
            print(f"{url} - Score: {score:.4f}\nSnippet: {snippet}\n")
