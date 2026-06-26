"""
Grounded Generation: Generate answers with verified citations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.citation_verifier import CitationVerifier
import json

class ResponseGenerator:
    """Generate grounded answers with citations"""
    
    def __init__(self):
        self.retriever = HybridRetriever()
        self.verifier = CitationVerifier()
        self.chunks_loaded = False
    
    def load_chunks(self, chunk_file: str = "data/processed/all_chunks.json"):
        """Load chunks and build retrieval index"""
        with open(chunk_file) as f:
            chunks = json.load(f)
        
        self.retriever.build_index(chunks)
        self.chunks_loaded = True
    
    def generate_response(self, query: str, top_k: int = 3) -> dict:
        """
        Generate answer for query with verified citations
        """
        
        if not self.chunks_loaded:
            self.load_chunks()
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k, method="hybrid")
        
        if not retrieved_chunks:
            return {
                "answer": "I don't have information to answer this question.",
                "citations": [],
                "confidence": 0.0,
                "reasoning": "No relevant chunks found"
            }
        
        # Step 2: Build answer from top chunk
        best_chunk = retrieved_chunks[0]
        
        # Simple answer generation: extract first relevant sentence
        answer = f"Based on the documentation: {best_chunk['content'][:150]}..."
        
        # Step 3: Verify citations
        verified_citations = []
        
        for chunk in retrieved_chunks:
            verification = self.verifier.verify_citation(query, chunk['content'], answer)
            
            if verification['is_valid']:
                verified_citations.append({
                    "text": chunk['content'][:100] + "...",
                    "source": chunk['source'],
                    "chunk_id": chunk['chunk_id'],
                    "confidence": verification['confidence']
                })
        
        # Calculate overall confidence
        if verified_citations:
            overall_confidence = sum(c['confidence'] for c in verified_citations) / len(verified_citations)
        else:
            overall_confidence = 0.0
        
        return {
            "answer": answer,
            "citations": verified_citations,
            "confidence": float(overall_confidence),
            "retrieved_chunks_count": len(retrieved_chunks),
            "verified_citations_count": len(verified_citations),
            "reasoning": f"Retrieved {len(retrieved_chunks)} chunks, verified {len(verified_citations)} citations"
        }

# Test
if __name__ == "__main__":
    generator = ResponseGenerator()
    
    test_queries = [
        "How do I use dependency injection in FastAPI?",
        "What is middleware?",
        "How do I handle errors?"
    ]
    
    print("=" * 70)
    print("GROUNDED GENERATION TEST")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 70)
        
        response = generator.generate_response(query, top_k=3)
        
        print(f"\n✓ Answer: {response['answer'][:150]}...")
        print(f"✓ Confidence: {response['confidence']:.3f}")
        print(f"✓ Verified Citations: {response['verified_citations_count']}/{response['retrieved_chunks_count']}")
        
        for i, cite in enumerate(response['citations'], 1):
            print(f"\n  Citation {i}:")
            print(f"    Source: {cite['source']}")
            print(f"    Confidence: {cite['confidence']:.3f}")