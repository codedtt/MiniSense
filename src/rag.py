import os
import numpy as np


class SimpleFAQVectorStore:
    """Lightweight sentence-transformer RAG store using Cosine Similarity."""

    def __init__(self, raw_faq_path: str):
        self.raw_faq_path = raw_faq_path
        self.chunks = []
        self.embeddings = []
        self._load_and_chunk()

    def _load_and_chunk(self):
        with open(self.raw_faq_path, "r") as f:
            text = f.read()

        # Chunking Strategy: Split by double-newline to isolate Q&A blocks
        raw_blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        self.chunks = raw_blocks

        # Fallback dense embedding proxy using standard TF-IDF / Normalized feature vectors
        # for local zero-dependency runnability (Can replace with sentence-transformers/OpenAI)
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.vectorizer = TfidfVectorizer().fit(self.chunks)
        self.embeddings = self.vectorizer.transform(self.chunks).toarray()

    def retrieve(self, query: str, top_k: int = 3):
        query_vec = self.vectorizer.transform([query]).toarray()[0]
        norm_q = np.linalg.norm(query_vec)

        if norm_q == 0:
            return [
                {"text": self.chunks[i], "score": 0.0}
                for i in range(min(top_k, len(self.chunks)))
            ]

        scores = []
        for idx, doc_vec in enumerate(self.embeddings):
            norm_d = np.linalg.norm(doc_vec)
            sim = (
                np.dot(query_vec, doc_vec) / (norm_q * norm_d)
                if norm_d > 0
                else 0.0
            )
            scores.append((idx, float(sim)))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_results = []
        for idx, score in scores[:top_k]:
            top_results.append({"text": self.chunks[idx], "score": round(score, 4)})
        return top_results