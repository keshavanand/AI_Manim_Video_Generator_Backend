from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel


class SceneSchema(BaseModel):
    id: PydanticObjectId
    scene_name: str
    scene_code: Optional[str] = None
    scene_output: Optional[str] = None
    scene_prompt: Optional[str] = None

class RePrompt(BaseModel):
    scene_Id: PydanticObjectId
    code: Optional[str] = None
    prompt: str
    output: Optional[str] = None