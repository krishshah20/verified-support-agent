"""
Stateful Multi-Agent Orchestrator with Memory
Now tracks conversation history and past cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.orchestrator import AgentOrchestrator
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory

class StatefulOrchestrator:
    """Orchestrator with memory capabilities"""
    
    def __init__(self, conversation_id: str = "default"):
        self.orchestrator = AgentOrchestrator()
        self.short_term = ShortTermMemory(conversation_id)
        self.long_term = LongTermMemory()
        self.conversation_id = conversation_id
    
    def process_query(self, query: str) -> dict:
        """Process query with memory awareness"""
        
        print(f"\n{'='*70}")
        print(f"STATEFUL ORCHESTRATION (Conversation: {self.conversation_id})")
        print(f"{'='*70}")
        
        # Step 1: Add user message to short-term memory
        self.short_term.add_message("user", query)
        
        # Step 2: Search long-term memory for similar past cases
        print(f"\n[MEMORY] Searching past cases...")
        similar_cases = self.long_term.find_similar_cases(query, top_k=2)
        
        # Step 3: Run agent pipeline
        print(f"\n[AGENT] Running orchestration...")
        response = self.orchestrator.run(query)
        
        # Step 4: Add assistant response to short-term memory
        self.short_term.add_message("assistant", response["answer"])
        
        # Step 5: Store successful case in long-term memory
        if response["status"] == "approved":
            self.long_term.store_case(
                query=query,
                answer=response["answer"],
                confidence=response["retrieval_confidence"],
                metadata={
                    "critic_confidence": response["critic_confidence"],
                    "status": response["status"]
                }
            )
        
        # Step 6: Build final response with memory context
        final_response = {
            **response,
            "conversation_id": self.conversation_id,
            "similar_past_cases": similar_cases,
            "short_term_summary": self.short_term.get_summary(),
            "memory_stats": self.long_term.get_statistics()
        }
        
        return final_response
    
    def get_conversation_summary(self) -> str:
        """Get full conversation summary"""
        return self.short_term.get_summary()
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        return self.long_term.get_statistics()

# Test
if __name__ == "__main__":
    print("\n" + "="*70)
    print("STATEFUL ORCHESTRATOR TEST (Multi-turn Conversation)")
    print("="*70)
    
    orchestrator = StatefulOrchestrator(conversation_id="conv_001")
    
    # Multi-turn conversation
    queries = [
        "How do I use dependency injection in FastAPI?",
        "Can you give me a code example?",
        "What is middleware?"
    ]
    
    for query in queries:
        result = orchestrator.process_query(query)
        
        print(f"\n{'='*70}")
        print(f"RESPONSE SUMMARY")
        print(f"{'='*70}")
        print(f"Status: {result['status']}")
        print(f"Retrieval Confidence: {result['retrieval_confidence']:.1%}")
        print(f"Should Escalate: {result['should_escalate']}")
        
        if result['similar_past_cases']:
            print(f"\nSimilar Past Cases: {len(result['similar_past_cases'])}")
            for case in result['similar_past_cases']:
                print(f"  - {case['case_id']}: {case['similarity']:.2f} similarity")
        
        print(f"\nMemory Stats:")
        stats = result['memory_stats']
        print(f"  Total cases stored: {stats['total_cases']}")
        print(f"  Avg confidence: {stats['avg_confidence']:.2f}")