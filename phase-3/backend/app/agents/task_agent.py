# app/agents/task_agent.py
from app.db.session import get_session
from app.config import settings
from app.schemas.chat import ChatRequest
import requests
import os

class TaskAgent:
    """
    Handles AI chat interactions.
    """
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment")

    def chat(self, session, user_id: int, message: str, conversation_history: list) -> str:
        """
        Sends the message to Groq API (LLaMA 3.3) and returns the response.
        """
        url = "https://api.groq.ai/v1/llama-3.3-70b-versatile/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "input": message
        }
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("output", [""])[0]
        except Exception as e:
            raise RuntimeError(f"Groq API call failed: {str(e)}")
