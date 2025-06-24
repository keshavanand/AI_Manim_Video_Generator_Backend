from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel
from datetime import datetime

class SceneSchema(BaseModel):
    id: PydanticObjectId
    scene_name: Optional[str] =None
    scene_code: Optional[str] = None
    scene_output: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RePrompt(BaseModel):
    scene_Id: PydanticObjectId
    code: Optional[str] = None
    prompt: str
    output: Optional[str] = None

class AddSceneSchema(BaseModel):
    project_id: PydanticObjectId
    scene_prompt: str