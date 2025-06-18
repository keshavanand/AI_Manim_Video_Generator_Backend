# Pydantic schemas for manim input/output
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId

class RePrompt(BaseModel):
    scene_Id: PydanticObjectId
    code: Optional[str] = None
    prompt: str
    output: Optional[str] = None

class CreateProject(BaseModel):
    title: str
    description: Optional[str] = None
    prompt: str

class UpdateProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class UpdateScene(BaseModel):
    scene_name: Optional[str]
    scene_code: Optional[str]

class SceneSchema(BaseModel):
    id: PydanticObjectId
    scene_name: str
    scene_code: Optional[str] = None
    scene_output: Optional[str] = None
    scene_prompt: Optional[str] = None

class Project(BaseModel):
    id: PydanticObjectId
    title: Optional[str]
    description: Optional[str]