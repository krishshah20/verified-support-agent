import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.stateful_orchestrator import StatefulOrchestrator

print("="*70)
print("WEEK 2 DAYS 10-12: MEMORY SYSTEMS TEST")
print("="*70)

orchestrator = StatefulOrchestrator(conversation_id="conv_001")

queries = [
    "How do I use dependency injection in FastAPI?",
    "What about error handling?",
    "Tell me about middleware"
]

for i, query in enumerate(queries, 1):
    print(f"\n[TURN {i}] User: {query}")
    result = orchestrator.process_query(query)
    
    print(f"\n  Status: {result['status']}")
    print(f"  Cases in memory: {result['memory_stats']['total_cases']}")
    
    if result['similar_past_cases']:
        print(f"  Similar past cases found: {len(result['similar_past_cases'])}")

print(f"\n{'='*70}")
print("Final Conversation Summary:")
print(f"{'='*70}")
print(orchestrator.get_conversation_summary())