from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.config import settings

class SimilarityEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )

    def calculate_similarity(self, input_text: str, articles: list) -> list:
        if not articles:
            return []

        corpus = [input_text]
        for a in articles:
            text = f"{a.get('title','')} {a.get('description','')}"
            corpus.append(text)

        try:
            tfidf = self.vectorizer.fit_transform(corpus)
            scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        except Exception:
            scores = np.zeros(len(articles))

        for idx, a in enumerate(articles):
            a['similarity_score'] = float(scores[idx])
        return articles

    def find_best_match(self, input_text: str, articles: list) -> tuple:
        scored = self.calculate_similarity(input_text, articles)
        if not scored:
            return None, 0.0
        best = max(scored, key=lambda x: x.get('similarity_score', 0.0))
        score = best.get('similarity_score', 0.0)
        if score < settings.SIMILARITY_THRESHOLD:
            return None, 0.0
        return best, score