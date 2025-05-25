import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self, data_path):
        with open(data_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

        self.urls = [entry[0] for entry in self.data]
        self.texts = [entry[1] for entry in self.data]

        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.doc_vectors = self.vectorizer.fit_transform(self.texts)

    def search(self, query, top_k=5):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.doc_vectors).flatten()
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for i in top_indices:
            snippet = SearchEngine.search_snippet(self.texts[i], query)
            results.append((self.urls[i], scores[i], snippet))
        return results
    
    def search_snippet(text, query, window_size=30):
        pattern = re.escape(query.lower())
        matches = re.search(pattern, text.lower())
        if matches:
            start = max(matches.start() - window_size, 0)
            end = min(matches.end() + window_size, len(text))
            snippet = text[start:end]
            return "..." + snippet.strip() + "..."
        else:
            return text[:2*window_size] + "..."
    
if __name__ == "__main__":
    search_engine = SearchEngine('prepared_data.json')
    query = input("Enter your search query: ")
    results = search_engine.search(query)
    for url, score, snippet in results:
        print(f"{url} - Score: {score:.4f}\nSnippet: {snippet}\n")
