import os
import requests

class TaskAgent:
    """Handles AI chat interactions."""
    
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment")

    def chat(self, session, user_id: int, message: str, conversation_history: list) -> str:
        """
        Calls Groq API using OpenAI-compatible chat completions endpoint.
        Returns the model response string.
        """

        # ✅ New correct Groq endpoint
        url = "https://api.groq.com/openai/v1/chat/completions"

        # 🧱 Build messages (optional chat history support)
        messages = [{"role": "user", "content": message}]
        # If you want history, you can extend messages with conversation_history

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 🧩 Extract response (OpenAI style)
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"Groq API call failed: {e}")
