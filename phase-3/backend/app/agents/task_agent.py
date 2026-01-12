# app/agents/task_agent.py

import os
import requests
from typing import List, Dict

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


class TaskAgent:
    """
    TaskAgent handles AI chat interactions using Groq's LLaMA 3.3 API.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment variables")
        self.api_url = "https://api.groq.ai/v1/llama-3.3-70b-versatile/completions"
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def chat(
        self,
        session,               # SQLModel Session (not used in agent but kept for future DB logic)
        user_id: int,          # Current user ID
        message: str,          # User message
        conversation_history: List[Dict[str, str]] = None  # [{"role": "user", "content": "..."}]
    ) -> str:
        """
        Sends user message + conversation history to Groq API and returns AI response.
        """
        conversation_history = conversation_history or []

        # Build input text for Groq
        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in conversation_history
        )
        full_input = f"{history_text}\nuser: {message}" if history_text else f"user: {message}"

        payload = {
            "model": "llama-3.3-70b-versatile",
            "input": full_input
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Groq returns 'output' as a list of strings
            output_list = data.get("output", [])
            if not output_list:
                return "⚠️ Groq API returned empty response."
            return output_list[0]
        except requests.exceptions.RequestException as e:
            # Catch network/API errors
            print(f"❌ Groq API request failed: {e}")
            return "⚠️ Failed to get response from AI service."
