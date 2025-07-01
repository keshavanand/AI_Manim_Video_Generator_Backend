# Interface with OpenAI or local LLM
import os
from google import genai
from google.genai import types
from app.core import settings
from google.genai.types import Content, Part
from app.schemas import LLMResponse
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


def generate_code_new(user_prompt:str, base_prompt:str,system_prompt:str, modifications: str ="") -> types.GenerateContentResponse:
    """Send prompt to Gemini LLM and return response."""

    combined_prompt = f"{base_prompt.strip()}\n\n{modifications.strip()}\n\n{user_prompt.strip()}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[LLMResponse],
            "system_instruction": system_prompt,
            },
        contents=combined_prompt,
    )

    return response
