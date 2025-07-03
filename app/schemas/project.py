# Pydantic schemas for manim input/output
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models import ProjectStatus
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
    status: ProjectStatus
    error: Optional[str] = None
    project_path: Optional[Path] = None

class ProjectPrompt(BaseModel):
    prompt: str 
  
class DiffModification(BaseModel):
  path: str
  type: Literal["diff", "file"]
  # Only for type="diff"
  diff: Optional[str] = None
  # Only for type="file"
  status: Optional[Literal["created", "updated", "deleted"]] = None
  content: Optional[str] = None

class DiffRequest(BaseModel):
  modifications: List[DiffModification]
