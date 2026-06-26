"""
Hybrid Retrieval: Dense + Sparse combined
"""

import json
from pathlib import Path
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.bm25_index import BM25Index
import numpy as np

class HybridRetriever:
    """Combine dense (semantic) + sparse (keyword) retrieval"""
    
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.bm25 = BM25Index()
        self.dense_embeddings = []
        self.chunks = []
    
    def build_index(self, chunks: list):
        """Build both dense and sparse indices"""
        print("Building hybrid index...")
        
        self.chunks = chunks
        
        # Build BM25 index
        print("  [1/2] Building BM25 sparse index...")
        self.bm25.build_index(chunks)
        
        # Embed all chunks for dense retrieval
        print("  [2/2] Embedding chunks for dense retrieval...")
        texts = [chunk["content"] for chunk in chunks]
        self.dense_embeddings = self.embedder.embed_documents(texts)
        
        print(f"✓ Hybrid index ready: {len(chunks)} chunks")
    
    def retrieve(self, query: str, top_k: int = 5, method: str = "hybrid") -> list:
        """
        Retrieve using:
        - dense: semantic similarity only
        - sparse: BM25 keyword matching only
        - hybrid: combine both
        """
        
        if method == "dense":
            return self._dense_retrieve(query, top_k)
        elif method == "sparse":
            return self.bm25.search(query, top_k)
        elif method == "hybrid":
            return self._hybrid_retrieve(query, top_k)
    
    def _dense_retrieve(self, query: str, top_k: int) -> list:
        """Dense retrieval using embeddings"""
        query_embedding = self.embedder.embed_text(query)
        
        # Calculate cosine similarity
        similarities = []
        for i, chunk_embedding in enumerate(self.dense_embeddings):
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk_idx, score in similarities[:top_k]:
            chunk = self.chunks[chunk_idx]
            results.append({
                "chunk_id": chunk["id"],
                "content": chunk["content"],
                "source": chunk["source"],
                "score": float(score),
                "retrieval_method": "dense"
            })
        
        return results
    
    def _hybrid_retrieve(self, query: str, top_k: int) -> list:
        """Hybrid: combine dense + sparse scores"""
        
        # Get both results
        dense_results = self._dense_retrieve(query, top_k * 2)
        sparse_results = self.bm25.search(query, top_k * 2)
        
        # Normalize scores to 0-1
        dense_scores = {r["chunk_id"]: r["score"] for r in dense_results}
        sparse_scores = {r["chunk_id"]: r["score"] for r in sparse_results}
        
        # Combine: 60% dense + 40% sparse (weights)
        combined = {}
        for chunk in self.chunks:
            chunk_id = chunk["id"]
            dense_score = dense_scores.get(chunk_id, 0)
            sparse_score = sparse_scores.get(chunk_id, 0)
            
            # Normalize sparse score (BM25 is unbounded)
            if sparse_results:
                max_sparse = max(r["score"] for r in sparse_results)
                sparse_score = sparse_score / max_sparse if max_sparse > 0 else 0
            
            combined_score = 0.6 * dense_score + 0.4 * sparse_score
            
            if combined_score > 0:
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "dense_score": float(dense_score),
                    "sparse_score": float(sparse_score),
                    "combined_score": float(combined_score),
                    "retrieval_method": "hybrid"
                }
        
        # Sort and return top_k
        results = sorted(combined.values(), key=lambda x: x["combined_score"], reverse=True)
        return results[:top_k]

# Test
if __name__ == "__main__":
    # Load chunks
    with open("data/processed/all_chunks.json") as f:
        chunks = json.load(f)
    
    # Build hybrid index
    retriever = HybridRetriever()
    retriever.build_index(chunks)
    
    # Test queries
    test_queries = [
        "How do I use dependency injection in FastAPI?",
        "What is middleware in FastAPI?",
        "How do I handle errors in FastAPI?"
    ]
    
    print("\n" + "=" * 60)
    print("HYBRID RETRIEVAL TEST")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 60)
        
        results = retriever.retrieve(query, top_k=3, method="hybrid")
        
        for i, result in enumerate(results, 1):
            print(f"\n  [{i}] Score: {result['combined_score']:.3f}")
            print(f"      (Dense: {result['dense_score']:.3f}, Sparse: {result['sparse_score']:.3f})")
            print(f"      Source: {result['source']}")
            print(f"      Preview: {result['content'][:100]}...")