# app/agents/task_agent.py
import requests
from app.config import settings

class TaskAgent:
    def __init__(self, groq_api_key: str | None = None):
        # Use key from settings if not passed
        self.groq_api_key = groq_api_key or settings.GROQ_API_KEY
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set!")

    def chat(self, session, user_id: int, message: str, conversation_history: list):
        # Example API call to Groq
        url = "https://api.groq.ai/v1/llama-3.3-70b-versatile/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "input": message,
            "history": conversation_history
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # Extract text from response (depends on Groq format)
        return data.get("output", "")
