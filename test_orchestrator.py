import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Importing...")
from src.agent.orchestrator import AgentOrchestrator
print("✓ Import successful")

print("\nStep 2: Creating orchestrator...")
orchestrator = AgentOrchestrator()
print("✓ Orchestrator created")

print("\nStep 3: Running query...")
query = "How do I use dependency injection in FastAPI?"
result = orchestrator.run(query)
print("✓ Query completed")

print(f"\n📊 Final Result:")
print(f"  Status: {result['status']}")
print(f"  Should Escalate: {result['should_escalate']}")