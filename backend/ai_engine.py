import google.generativeai as genai
from config import GEMINI_API_KEY, AI_MODEL, TEMPERATURE
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, api_key: str):
        """Initialize the AI Engine with Gemini API"""
        if not api_key:
            logger.warning("No Gemini API key provided. AI features will be limited.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(AI_MODEL)
            self.enabled = True
            self.conversation_history = []
            logger.info(f"AI Engine initialized with model: {AI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize AI Engine: {e}")
            self.enabled = False

    def chat(self, message: str, context: Optional[str] = None) -> str:
        """Send a chat message and get AI response"""
        if not self.enabled:
            return "AI engine is not available. Please configure Gemini API key."
        
        try:
            # Build conversation with context
            full_message = message
            if context:
                full_message = f"Context: {context}\n\nMessage: {message}"
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Generate response
            response = self.model.generate_content(full_message)
            
            if response.text:
                self.conversation_history.append({"role": "ai", "content": response.text})
                return response.text
            else:
                return "No response generated"
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error: {str(e)}"

    def summarize(self, text: str) -> str:
        """Summarize provided text"""
        if not self.enabled:
            return "AI engine is not available."
        
        try:
            prompt = f"""Please summarize the following text in 3-5 sentences:

{text}

Summary:"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return f"Error: {str(e)}"

    def analyze(self, text: str, task: str = "analyze") -> dict:
        """Analyze text for various tasks"""
        if not self.enabled:
            return {"error": "AI engine is not available."}
        
        try:
            if task == "sentiment":
                prompt = f"Analyze the sentiment of this text and provide a detailed analysis:\n\n{text}"
            elif task == "keywords":
                prompt = f"Extract the main keywords from this text:\n\n{text}"
            elif task == "explanation":
                prompt = f"Explain this text in simpler terms:\n\n{text}"
            else:
                prompt = f"Analyze this text:\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return {"result": response.text, "task": task}
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"error": str(e)}

    def generate_ideas(self, topic: str, count: int = 5) -> list:
        """Generate creative ideas on a topic"""
        if not self.enabled:
            return []
        
        try:
            prompt = f"Generate {count} creative ideas for: {topic}"
            response = self.model.generate_content(prompt)
            
            # Parse ideas from response
            ideas = response.text.split('\n')
            ideas = [idea.strip() for idea in ideas if idea.strip()]
            return ideas[:count]
        except Exception as e:
            logger.error(f"Idea generation error: {e}")
            return []

    def explain_concept(self, concept: str) -> str:
        """Explain a technical concept"""
        if not self.enabled:
            return "AI engine is not available."
        
        try:
            prompt = f"""Please explain the following concept in a clear and concise way:
            
{concept}

Explanation:"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Explanation error: {e}")
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_history(self):
        """Get conversation history"""
        return self.conversation_history
