"""
Long-term Memory: Past resolved cases
Stores: previous Q&A, embeddings, resolutions
Searches: similar past cases for context
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from src.retrieval.embeddings import EmbeddingModel
import numpy as np

class LongTermMemory:
    """Store and retrieve past resolved cases"""
    
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.cases: list = []
        self.case_embeddings: list = []
    
    def store_case(self, query: str, answer: str, confidence: float, metadata: dict = None):
        """Store a resolved case"""
        
        # Create case record
        case = {
            "id": f"case_{len(self.cases)}",
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Embed the query for future similarity search
        embedding = self.embedder.embed_text(query)
        
        self.cases.append(case)
        self.case_embeddings.append(embedding)
        
        print(f"  [LONG-TERM] Stored case {case['id']}")
    
    def find_similar_cases(self, query: str, top_k: int = 3) -> list:
        """Find similar past cases"""
        
        if not self.cases:
            return []
        
        # Embed the query
        query_embedding = np.array(self.embedder.embed_text(query))
        
        # Calculate similarity to all stored cases
        similarities = []
        for i, case_emb in enumerate(self.case_embeddings):
            case_emb = np.array(case_emb)
            
            # Cosine similarity
            similarity = np.dot(query_embedding, case_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(case_emb) + 1e-10
            )
            
            similarities.append((i, similarity))
        
        # Sort and get top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:top_k]:
            if score > 0.5:  # Only include relevant cases
                case = self.cases[idx]
                results.append({
                    "case_id": case["id"],
                    "query": case["query"],
                    "answer": case["answer"],
                    "confidence": case["confidence"],
                    "similarity": float(score)
                })
        
        if results:
            print(f"  [LONG-TERM] Found {len(results)} similar cases")
        
        return results
    
    def get_statistics(self) -> dict:
        """Get memory statistics"""
        if not self.cases:
            return {"total_cases": 0, "avg_confidence": 0}
        
        confidences = [c["confidence"] for c in self.cases]
        
        return {
            "total_cases": len(self.cases),
            "avg_confidence": np.mean(confidences),
            "max_confidence": np.max(confidences),
            "min_confidence": np.min(confidences)
        }

# Test
if __name__ == "__main__":
    memory = LongTermMemory()
    
    print("Testing Long-term Memory:")
    print("=" * 60)
    
    # Store some cases
    print("\nStoring cases...")
    memory.store_case(
        query="How do I use dependency injection in FastAPI?",
        answer="Dependency injection allows you to declare dependencies...",
        confidence=0.88
    )
    
    memory.store_case(
        query="What is middleware in FastAPI?",
        answer="Middleware is a function that works with every request...",
        confidence=0.92
    )
    
    memory.store_case(
        query="How do I handle errors?",
        answer="Use exception handlers to catch and respond to errors...",
        confidence=0.85
    )
    
    # Search for similar cases
    print("\nSearching for similar cases...")
    query = "Can you explain dependency management in FastAPI?"
    results = memory.find_similar_cases(query, top_k=2)
    
    print(f"\nSimilar cases for: '{query}'")
    for result in results:
        print(f"  Case {result['case_id']}: Similarity {result['similarity']:.2f}")
        print(f"    Q: {result['query'][:50]}...")
        print(f"    A: {result['answer'][:50]}...")
    
    # Statistics
    print(f"\nMemory Statistics:")
    stats = memory.get_statistics()
    print(f"  Total cases: {stats['total_cases']}")
    print(f"  Avg confidence: {stats['avg_confidence']:.2f}")