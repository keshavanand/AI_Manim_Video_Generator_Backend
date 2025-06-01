# Pydantic schemas for manim input/output
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId
class Re_prompt(BaseModel):
    scene_Id: PydanticObjectId
    code: Optional[str] = None
    prompt: str
    output: Optional[str] = None