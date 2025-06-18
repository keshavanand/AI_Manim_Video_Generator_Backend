import json
import re
from typing import List, Dict, Any

def parse_gemini_response(response: str) -> List[Dict[str, Any]]:
    """Parse Gemini LLM response to a list of scene dicts."""
    cleaned = re.sub(r"```json\s*", "", response)
    cleaned = re.sub(r"\s*```", "", cleaned)
    try:
        scenes = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return []
    return scenes

def parse_single_scene(response: str) -> Dict[str, Any]:
    """Parse a single scene JSON from LLM response."""
    cleaned = re.sub(r"```json\s*", "", response)
    cleaned = re.sub(r"\s*```", "", cleaned)
    try:
        scene = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return {}
    return scene
