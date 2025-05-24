import json
import re

def parse_gemini_response(response: str)->list[dict]:
    cleaned = re.sub(r"```json\s*", "", response)
    cleaned = re.sub(r"\s*```", "", cleaned)

    try:
        scenes=json.loads(cleaned)

    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return []
    
    return scenes

