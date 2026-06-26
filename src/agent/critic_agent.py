"""
Critic Agent: Validates retrieval results
Checks: Is the answer correct? Is it complete? Confident?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.citation_verifier import CitationVerifier
import numpy as np

class CriticAgent:
    """Evaluate and validate answers"""
    
    def __init__(self):
        self.verifier = CitationVerifier()
    
    def evaluate(self, query: str, answer: str, citations: list) -> dict:
        """
        Evaluate answer quality
        Returns: {is_valid, confidence, feedback}
        """
        
        print(f"\n  [CRITIC] Evaluating answer...")
        print(f"  [CRITIC] Query: {query[:60]}...")
        print(f"  [CRITIC] Citations provided: {len(citations)}")
        
        # Check 1: Do we have citations?
        has_citations = len(citations) > 0
        
        if not has_citations:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "feedback": "No citations provided. Answer lacks grounding."
            }
        
        # Check 2: Are citations high quality?
        citation_confidences = [c['confidence'] for c in citations]
        avg_citation_confidence = np.mean(citation_confidences)
        
        print(f"  [CRITIC] Citation confidences: {[f'{c:.2f}' for c in citation_confidences]}")
        print(f"  [CRITIC] Average: {avg_citation_confidence:.2f}")
        
        # Check 3: Does answer length make sense?
        answer_words = len(answer.split())
        answer_length_ok = 50 < answer_words < 1000
        
        print(f"  [CRITIC] Answer length: {answer_words} words")
        
        # Determine validity
        is_valid = (
            has_citations and 
            avg_citation_confidence > 0.5 and 
            answer_length_ok
        )
        
        # Feedback
        feedback_parts = []
        if not has_citations:
            feedback_parts.append("Missing citations")
        if avg_citation_confidence < 0.5:
            feedback_parts.append("Low citation confidence")
        if not answer_length_ok:
            feedback_parts.append("Answer length unusual")
        
        feedback = ", ".join(feedback_parts) if feedback_parts else "Answer validated"
        
        return {
            "is_valid": is_valid,
            "confidence": float(avg_citation_confidence),
            "feedback": feedback,
            "num_citations": len(citations),
            "avg_citation_confidence": float(avg_citation_confidence)
        }

# Test
if __name__ == "__main__":
    critic = CriticAgent()
    
    # Test case: Good answer with citations
    query = "How do I use dependency injection?"
    answer = "Dependency injection in FastAPI allows you to declare dependencies..."
    citations = [
        {"confidence": 0.82, "text": "...", "source": "docs"},
        {"confidence": 0.75, "text": "...", "source": "docs"}
    ]
    
    result = critic.evaluate(query, answer, citations)
    
    print(f"\nCritic Evaluation Result:")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Feedback: {result['feedback']}")