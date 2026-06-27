"""Answer Synthesizer: Use Modern Google GenAI API to expand chunks into full answers"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import os
from dotenv import load_dotenv

load_dotenv()

class AnswerSynthesizer:
    """Synthesize comprehensive answers from chunks using modern Google GenAI API"""
        
    def __init__(self):
        # Modern client automatically looks for GEMINI_API_KEY or GOOGLE_API_KEY
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                
        if not self.api_key:
            print("⚠️  GEMINI_API_KEY / GOOGLE_API_KEY not set in .env")
            raise ValueError("Missing Google API Key")
                
        # Modern 2026 Import and Client Setup
        from google import genai
        self.client = genai.Client(api_key=self.api_key)
        # Using the standard, highly efficient production model
        self.model_name = "gemini-3.5-flash"

    def synthesize_answer(self, query: str, chunks: list) -> str:
        """Use Gemini to write comprehensive answer from chunks"""
                
        # Format chunks as context
        chunk_context = "\n\n".join([
            f"[Source {i+1}] {chunk['content']}"
            for i, chunk in enumerate(chunks[:3])
        ])
                
        # Create prompt
        prompt = f"""Based on the following documentation excerpts, write a comprehensive answer to the user's question.

Question: {query}

Documentation:
{chunk_context}

Instructions:
1. Write a detailed answer (minimum 100 words)
2. Explain the concept clearly
3. Include practical examples if relevant
4. Be specific and accurate
5. Reference the documentation sources

Answer:"""
                
        print(f"  [SYNTHESIZER] Generating answer with modern Gemini API...")
                
        try:
            # Modern generation syntax: client.models.generate_content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            answer = response.text.strip()
            word_count = len(answer.split())
            print(f"  [SYNTHESIZER] Generated {word_count} words ✓")
            return answer
                
        except Exception as e:
            print(f"  [SYNTHESIZER] Error: {str(e)}")
            return self._fallback_answer(query, chunks)

    def _fallback_answer(self, query: str, chunks: list) -> str:
        """Fallback: Combine chunks manually if API fails"""
        answer_parts = [f"Based on the documentation:\n"]
                
        for chunk in chunks[:3]:
            content = chunk['content']
            if len(content) < 200:
                answer_parts.append(content)
            else:
                answer_parts.append(content[:300])
                
        answer = "\n\n".join(answer_parts)
        if len(answer.split()) < 50:
            answer += "\n\nFor more information, please refer to the official documentation."
        return answer

# Test execution block
if __name__ == "__main__":
    synthesizer = AnswerSynthesizer()
        
    test_chunks = [
        {"content": "Dependency injection in FastAPI allows you to declare dependencies that FastAPI will automatically resolve for you."},
        {"content": "You can use the Depends function to declare a dependency in FastAPI."},
        {"content": "This makes your code more testable and modular."}
    ]
        
    query = "How do I use dependency injection in FastAPI?"
    answer = synthesizer.synthesize_answer(query, test_chunks)
        
    print(f"\nSynthesized Answer:")
    print(f"{'='*70}")
    print(answer)
    print(f"{'='*70}")
    print(f"Word count: {len(answer.split())}")