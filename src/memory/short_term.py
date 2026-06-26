"""
Short-term Memory: Current conversation state
Stores: conversation history, context, current task state
"""

import json
from datetime import datetime
from typing import List, Dict

class ShortTermMemory:
    """In-memory conversation state"""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.messages: List[Dict] = []
        self.context = {}
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add message to conversation history"""
        message = {
            "role": role,  # "user", "assistant", "system"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        print(f"  [SHORT-TERM] Added {role} message")
    
    def get_history(self, limit: int = 5) -> List[Dict]:
        """Get last N messages"""
        return self.messages[-limit:]
    
    def set_context(self, key: str, value: any):
        """Store context variable"""
        self.context[key] = value
    
    def get_context(self, key: str) -> any:
        """Retrieve context variable"""
        return self.context.get(key)
    
    def get_summary(self) -> str:
        """Get conversation summary for agent context"""
        if not self.messages:
            return "No conversation history yet"
        
        summary_parts = []
        for msg in self.messages[-3:]:  # Last 3 messages
            summary_parts.append(f"{msg['role']}: {msg['content'][:60]}...")
        
        return "\n".join(summary_parts)
    
    def clear(self):
        """Clear conversation"""
        self.messages = []
        self.context = {}

# Test
if __name__ == "__main__":
    memory = ShortTermMemory("conv_001")
    
    print("Testing Short-term Memory:")
    print("=" * 60)
    
    # Add messages
    memory.add_message("user", "How do I use dependency injection?")
    memory.add_message("assistant", "Dependency injection allows you to declare dependencies...")
    memory.add_message("user", "Can you give me an example?")
    
    # Store context
    memory.set_context("last_topic", "dependency_injection")
    memory.set_context("user_level", "beginner")
    
    # Retrieve
    print(f"\nConversation Summary:")
    print(memory.get_summary())
    
    print(f"\nContext:")
    print(f"  Last topic: {memory.get_context('last_topic')}")
    print(f"  User level: {memory.get_context('user_level')}")
    
    print(f"\nFull history:")
    for msg in memory.get_history():
        print(f"  {msg['role']}: {msg['content'][:50]}...")