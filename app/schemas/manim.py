# Pydantic schemas for manim input/output
from pydantic import BaseModel

class Re_prompt(BaseModel):
    original_prompt: str
    scene_name:str
    code: str
    prompt: str
    output: str | None = ""