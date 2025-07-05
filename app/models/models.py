from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document, Link, PydanticObjectId
from pydantic import Field, EmailStr
from app.schemas.llm_response import LLMResponse

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

class ProjectStatus(str, Enum):
    queued= 'queued'
    processing = 'processing'
    complete = "complete"
    error = "error"
class Project(Document):
    """Project containing multiple scenes."""
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    owner: Link[User]
    title: str = Field(index=True)
    status: ProjectStatus = ProjectStatus.queued
    error: Optional[str] = None
    project_path: Optional[str] = None
    manim_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    full_video_path: Optional[str] = None
    previous_files: Optional[LLMResponse] = None

    class Settings:
        name = "projects"

    def __str__(self):
        return f"Project(title={self.title}, owner={self.owner})"

class Status(str, Enum):
    pending = 'pending'
    generating = "generating"
    ready = "ready"
    error = "error"
class Scene(Document):
    """Scene generated from a prompt and code."""
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    scene_name: str = Field(index=True)
    scene_code: Optional[str] = None
    scene_output: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    status: Status = Status.pending
    video_path: Optional[str] = None
    scene_path: str
    owner: Link[User]
    project: Link[Project]
    class Settings:
        name = "scenes"
        indexes = [
                    [("scene_name", 1), ("project", 1)]  # compound index
                ]
    def __str__(self):
        return f"Scene(scene_name={self.scene_name}, project={self.project})"
    
class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(Document):
    role: ChatRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    project: Optional[Link[Project]]= None

    class Settings:
        name= "chat_messages"
        indexes = ["project"]

    def __str__(self):
        return f"{self.role}: {self.content[:30]}" 
    
class MediaType(str,Enum):
    video = "video"
    audio = "audio"
    image = "image"
    code = "code"
    output = "ouptut"
class Media(Document):
    type: MediaType
    path: str
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    #Links
    projects: Optional[Link[Project]] = None
    scene: Optional[Link[Scene]] = None
    is_final_output: bool = False # true for combined final video
    status: Status = Status.pending

    class Settings:
        name="media"

# Rebuild models for forward references
User.model_rebuild()
Project.model_rebuild()
Scene.model_rebuild()
ChatMessage.model_rebuild()
Media.model_rebuild()
