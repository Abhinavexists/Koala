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
        results = [(self.urls[i], scores[i]) for i in top_indices]
        return results
    
if __name__ == "__main__":
    search_engine = SearchEngine('prepared_data.json')
    query = input("Enter your search query: ")
    results = search_engine.search(query)
    for url, score in results:
        print(f"{url} - Score: {score:.4f}")
