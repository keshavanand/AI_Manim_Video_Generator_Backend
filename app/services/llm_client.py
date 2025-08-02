
# Interface with OpenAI or local LLM
import os
from google import genai
from google.genai import types
from app.core import settings
from google.genai.types import Content, Part
from app.schemas.llm_response import LLMResponse
from app.core.logging_config import logger
from app.services.updated_prompts import enhanced_promt
client = genai.Client(api_key=settings.GEMINI_API)

def generate_code(prompt: str) -> types.GenerateContentResponse:
    """Send prompt to Gemini LLM and return response."""
    try:
        logger.info("Sending prompt to Gemini LLM (v2.0-flash)")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution)]
            ),
            contents=prompt
        )
        logger.info("Received response from Gemini LLM (v2.0-flash)")
        return response
    except Exception as e:
        logger.error(f"Error in generate_code: {e}")
        raise

def generate_code_new(user_prompt: str, base_prompt: str, system_prompt: str, modifications: str = "") -> types.GenerateContentResponse:
    """Send prompt to Gemini LLM and return response."""
    try:
        combined_prompt = f"{base_prompt.strip()}\n\n{modifications.strip()}\n\n{user_prompt.strip()}"
        logger.info("Sending prompt to Gemini LLM (v2.5-flash)")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={
                "response_mime_type": "application/json",
                "response_schema": LLMResponse,
                "system_instruction": system_prompt,
            },
            contents=combined_prompt,
        )
        logger.info("Received response from Gemini LLM (v2.5-flash)")
        return response
    except Exception as e:
        logger.error(f"Error in generate_code_new: {e}")
        raise

def enahnce_prompt(prompt: str):
    prompt = f"This is user prompt: {prompt}\
            Enhanced it using following instructons: {enhanced_promt} "
    try:
        logger.info("Enhancing user prompt")
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt
        )
        for chunk in response:
            yield chunk.text
    except Exception as e:
        logger.error(f"Error in enhacning prompt: {e}")
        raise

        