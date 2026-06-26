import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.response_generator import ResponseGenerator

generator = ResponseGenerator()

test_queries = [
    "How do I use dependency injection in FastAPI?",
    "What is middleware?",
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