from typing import List, Optional
from pydantic import BaseModel


class FileEntry(BaseModel):
  file_name: str
  scene_name: str
  filePath: str
  status: str  # "created", "updated", or "deleted"
  content: Optional[str] = None  # Omit if status == "deleted"

class LLMResponse(BaseModel):
  id: str
  title: str
  files: List[FileEntry]
  commands: List[str]