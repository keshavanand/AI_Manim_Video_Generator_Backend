from datetime import datetime
from typing import Optional
from beanie import Document, Link, PydanticObjectId
from pydantic import Field, EmailStr

class User(Document):
    """User account model."""
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    username: str = Field(index=True)
    email: EmailStr = Field(index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "users"

    def __str__(self):
        return f"User(username={self.username}, email={self.email})"

class Project(Document):
    """Project containing multiple scenes."""
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    owner: Link[User]
    title: str = Field(index=True)
    description: Optional[str] = None
    original_prompt: str
    project_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    full_video_path: Optional[str] = None

    class Settings:
        name = "projects"

    def __str__(self):
        return f"Project(title={self.title}, owner={self.owner})"

class Scene(Document):
    """Scene generated from a prompt and code."""
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    scene_name: str = Field(index=True)
    scene_code: Optional[str] = None
    scene_output: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    scene_prompt: Optional[str] = None
    video_path: Optional[str] = None
    scene_path: str
    owner: Link[User]
    project: Link[Project]
    status: str = "pending"  # pending, running, completed, failed

    class Settings:
        name = "scenes"

    def __str__(self):
        return f"Scene(scene_name={self.scene_name}, project={self.project})"

# Rebuild models for forward references
User.model_rebuild()
Project.model_rebuild()
Scene.model_rebuild()
