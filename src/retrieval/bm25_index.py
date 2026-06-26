"""
Sparse Retrieval: TF-IDF keyword matching (simpler than BM25)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class BM25Index:
    """TF-IDF for keyword/phrase matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tfidf_matrix = None
        self.chunks = []
    
    def build_index(self, chunks: list):
        """Build TF-IDF index from chunks"""
        texts = [chunk["content"] for chunk in chunks]
        self.chunks = chunks
        
        # Build TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        print(f"✓ TF-IDF index built for {len(chunks)} chunks")
    
    def search(self, query: str, top_k: int = 5) -> list:
        """Search using TF-IDF"""
        # Transform query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include non-zero scores
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk["id"],
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "score": float(similarities[idx]),
                    "retrieval_method": "tfidf"
                })
        
        return results