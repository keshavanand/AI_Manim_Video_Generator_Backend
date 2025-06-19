# Pydantic schemas for manim input/output
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId

class CreateProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: str

class UpdateProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class UpdateScene(BaseModel):
    scene_name: Optional[str]
    scene_code: Optional[str]

class Project(BaseModel):
    id: PydanticObjectId
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None