import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def call_groq(input_text: str) -> str:
    """
    Calls Groq API for LLaMA 3.3 chat completion.
    Returns the AI-generated response as string.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")

    url = "https://api.groq.ai/v1/llama-3.3-70b-versatile/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "input": input_text
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # raises exception if API fails
    data = response.json()
    # Groq API usually returns "output" as list of strings
    return data.get("output", [""])[0]
