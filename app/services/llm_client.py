# Interface with OpenAI or local LLM
import os
from google import genai
from google.genai import types
from app.core import settings

client = genai.Client(api_key=settings.GEMINI_API)

def generate_code(prompt: str) -> types.GenerateContentResponse:
    """Send prompt to Gemini LLM and return response."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            tools=[types.Tool(code_execution=types.ToolCodeExecution)]
        ),
        contents=prompt
    )
    return response