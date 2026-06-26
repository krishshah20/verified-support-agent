"""
Citation Verification: Ensure chunks actually answer the question
"""

from src.retrieval.embeddings import EmbeddingModel
import numpy as np

class CitationVerifier:
    """Verify that a chunk actually supports an answer to the query"""
    
    def __init__(self):
        self.embedder = EmbeddingModel()
    
    def verify_citation(self, query: str, chunk_content: str, generated_answer: str) -> dict:
        """
        Check if chunk actually supports the answer
        Returns: {is_valid, confidence, reason}
        """
        
        # Get embeddings
        query_emb = np.array(self.embedder.embed_text(query))
        chunk_emb = np.array(self.embedder.embed_text(chunk_content))
        answer_emb = np.array(self.embedder.embed_text(generated_answer))
        
        # Calculate similarities
        query_chunk_sim = np.dot(query_emb, chunk_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb) + 1e-10
        )
        
        answer_chunk_sim = np.dot(answer_emb, chunk_emb) / (
            np.linalg.norm(answer_emb) * np.linalg.norm(chunk_emb) + 1e-10
        )
        
        # Verification logic
        # Both similarities should be high
        is_valid = query_chunk_sim > 0.5 and answer_chunk_sim > 0.5
        
        confidence = (query_chunk_sim + answer_chunk_sim) / 2
        
        reason = ""
        if query_chunk_sim < 0.5:
            reason = "Chunk doesn't address the query"
        elif answer_chunk_sim < 0.5:
            reason = "Chunk doesn't support the generated answer"
        else:
            reason = "Citation verified"
        
        return {
            "is_valid": is_valid,
            "confidence": float(confidence),
            "query_chunk_similarity": float(query_chunk_sim),
            "answer_chunk_similarity": float(answer_chunk_sim),
            "reason": reason
        }