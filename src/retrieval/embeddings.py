"""
Dense Retrieval: Embeddings
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

class EmbeddingModel:
    """Lightweight embedding model (no API key needed)"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # MiniLM: small, fast, 384-dim embeddings, free
        self.model = HuggingFaceEmbeddings(model_name=model_name)
    
    def embed_text(self, text: str) -> list:
        """Convert text to embedding vector"""
        return self.model.embed_query(text)
    
    def embed_documents(self, texts: list) -> list:
        """Convert multiple texts to embeddings"""
        return self.model.embed_documents(texts)

# Test
if __name__ == "__main__":
    embedder = EmbeddingModel()
    
    # Test embedding
    test_text = "How do I use FastAPI with dependency injection?"
    embedding = embedder.embed_text(test_text)
    
    print(f"Text: {test_text}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")