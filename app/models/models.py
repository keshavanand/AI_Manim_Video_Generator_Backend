# User DB model
from datetime import datetime
from pathlib import Path
from beanie import Document, PydanticObjectId
from typing import List, Optional
from pydantic import Field

class Scene(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    scene_name: str
    scene_code: Optional[str]
    scene_output: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scene_prompt: Optional[str]
    video_path: Optional[Path]

    class Settings:
        name= "scene"

class Project(Document):
    id : Optional[PydanticObjectId] = Field(default=None, alias="_id")
    title: str
    description: Optional[str]
    original_prompt: str
    scenes: List[Scene] = []
    project_path : Optional[Path]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class User(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    username: str
    email: str
    hashed_password: str
    projects: List[Project] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
