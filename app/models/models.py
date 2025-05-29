# User DB model
from datetime import datetime, timezone
from pathlib import Path
from beanie import Document, Link, PydanticObjectId
from typing import List, Optional, Dict
from bson import ObjectId
from pydantic import Field

class Scene(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    scene_name: str
    scene_code: Optional[str]= None
    scene_output: Optional[str]= None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scene_prompt: Optional[str]= None
    video_path: Optional[Path]= None
    scene_path: Path
    #  Add a reference to the Project it belongs to
    owner: Optional[Link["User"]] = None
    class Settings:
        name= "scene"

class Project(Document):
    id : Optional[PydanticObjectId] = Field(default=None, alias="_id")
    # Link to owner user
    owner: Link["User"] = None
    title: str
    description: Optional[str]= None
    original_prompt: str
    # List of scene links
    scenes: List[Link["Scene"]] = []
    scene_list: List[Dict] = []
    project_path : Optional[Path]= None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"

class User(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    username: str
    email: str
    hashed_password: str
    projects: List[Link["Project"]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

Scene.model_rebuild()
Project.model_rebuild()
User.model_rebuild()
