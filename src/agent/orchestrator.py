"""
Multi-Agent Orchestration using LangGraph
Supervisor → Retrieval → Critic
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
import json

class AgentState(TypedDict):
    """State passed between agents"""
    query: str
    retrieval_result: dict
    critic_result: dict
    final_response: dict

class AgentOrchestrator:
    """Orchestrate multi-agent system"""
    
    def __init__(self):
        from src.api.response_generator import ResponseGenerator
        from src.agent.critic_agent import CriticAgent
        
        self.retrieval_agent = ResponseGenerator()
        self.critic_agent = CriticAgent()
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build LangGraph state machine"""
        
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("supervisor", self._supervisor)
        workflow.add_node("retrieval", self._retrieval_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("finalize", self._finalize)
        
        # Define edges (flow)
        workflow.add_edge("supervisor", "retrieval")
        workflow.add_edge("retrieval", "critic")
        workflow.add_edge("critic", "finalize")
        workflow.add_edge("finalize", END)
        
        workflow.set_entry_point("supervisor")
        
        self.graph = workflow.compile()
    
    def _supervisor(self, state: AgentState) -> AgentState:
        """Supervisor: Analyze query type"""
        query = state["query"]
        
        print(f"\n[SUPERVISOR] Analyzing query: '{query}'")
        
        # Simple classification
        is_how_question = query.lower().startswith("how")
        is_what_question = query.lower().startswith("what")
        
        query_type = "how-to" if is_how_question else ("definition" if is_what_question else "general")
        
        print(f"[SUPERVISOR] Query type: {query_type}")
        
        return {
            **state,
            "query_type": query_type
        }
    
    def _retrieval_node(self, state: AgentState) -> AgentState:
        """Retrieval Agent: Get answer with citations"""
        query = state["query"]
        
        print(f"\n[RETRIEVAL] Searching for answer...")
        
        # Use Week 1 RAG
        response = self.retrieval_agent.generate_response(query, top_k=3)
        
        print(f"[RETRIEVAL] Found answer. Confidence: {response['confidence']:.1%}")
        
        return {
            **state,
            "retrieval_result": response
        }
    
    def _critic_node(self, state: AgentState) -> AgentState:
        """Critic Agent: Validate the answer"""
        query = state["query"]
        retrieval_result = state["retrieval_result"]
        
        print(f"\n[CRITIC] Validating answer...")
        
        answer = retrieval_result["answer"]
        citations = retrieval_result["citations"]
        
        # Critic evaluation
        critic_result = self.critic_agent.evaluate(
            query=query,
            answer=answer,
            citations=citations
        )
        
        print(f"[CRITIC] Validation: {critic_result['is_valid']} | Confidence: {critic_result['confidence']:.1%}")
        
        return {
            **state,
            "critic_result": critic_result
        }
    
    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize: Decide what to return"""
        retrieval = state["retrieval_result"]
        critic = state["critic_result"]
        
        print(f"\n[FINALIZE] Preparing final response...")
        
        if critic["is_valid"]:
            response_status = "approved"
        else:
            response_status = "needs_escalation"
        
        final_response = {
            "status": response_status,
            "answer": retrieval["answer"],
            "citations": retrieval["citations"],
            "retrieval_confidence": retrieval["confidence"],
            "critic_confidence": critic["confidence"],
            "critic_feedback": critic["feedback"],
            "should_escalate": not critic["is_valid"]
        }
        
        return {
            **state,
            "final_response": final_response
        }
    
    def run(self, query: str) -> dict:
        """Run the full agent pipeline"""
        print("\n" + "="*70)
        print("MULTI-AGENT ORCHESTRATION START")
        print("="*70)
        
        initial_state: AgentState = {
            "query": query,
            "retrieval_result": {},
            "critic_result": {},
            "final_response": {}
        }
        
        final_state = self.graph.invoke(initial_state)
        
        print("\n" + "="*70)
        print("MULTI-AGENT ORCHESTRATION COMPLETE")
        print("="*70)
        
        return final_state["final_response"]

# Test
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    test_queries = [
        "How do I use dependency injection in FastAPI?",
        "What is middleware?"
    ]
    
    for query in test_queries:
        result = orchestrator.run(query)
        
        print(f"\n📊 FINAL RESPONSE:")
        print(f"  Status: {result['status']}")
        print(f"  Answer: {result['answer'][:100]}...")
        print(f"  Retrieval Confidence: {result['retrieval_confidence']:.1%}")
        print(f"  Critic Confidence: {result['critic_confidence']:.1%}")
        print(f"  Should Escalate: {result['should_escalate']}")
        print()