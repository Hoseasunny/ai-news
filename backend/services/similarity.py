from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.config import settings
from typing import Optional

class SimilarityEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self._embedder = self._load_embedder()

    def _load_embedder(self) -> Optional[object]:
        if not settings.USE_EMBEDDINGS:
            return None
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            return None

    def _embed_similarity(self, input_text: str, articles: list) -> Optional[np.ndarray]:
        if not self._embedder or not articles:
            return None
        texts = [input_text] + [f"{a.get('title','')} {a.get('description','')}" for a in articles]
        try:
            vectors = self._embedder.encode(texts, normalize_embeddings=True)
            input_vec = vectors[0:1]
            article_vecs = vectors[1:]
            scores = (input_vec @ article_vecs.T).flatten()
            return scores
        except Exception:
            return None

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

        embed_scores = self._embed_similarity(input_text, articles)
        if embed_scores is not None:
            scores = (0.6 * scores) + (0.4 * embed_scores)

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

    def pairwise_similarity(self, articles: list) -> float:
        if len(articles) < 2:
            return 0.0
        texts = [f"{a.get('title','')} {a.get('description','')}" for a in articles[:3]]
        try:
            tfidf = self.vectorizer.fit_transform(texts)
            sims = cosine_similarity(tfidf)
            # average upper triangle excluding diagonal
            total = 0.0
            count = 0
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    total += sims[i][j]
                    count += 1
            return float(total / count) if count else 0.0
        except Exception:
            return 0.0
