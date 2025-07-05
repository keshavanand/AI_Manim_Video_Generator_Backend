from typing import Annotated
from fastapi import APIRouter, Depends
from app.core import get_current_user
from app.models import ChatMessage, User as User_model, Project as Project_model

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/history/{id}", response_model=list[ChatMessage])
async def get_chat_history(id) -> list[ChatMessage]:
    """
    Get the chat history for the current project.
    """
    project = await Project_model.get(id)
    # Fetch chat messages for the current user
    chat_messages = await ChatMessage.find(
        ChatMessage.project.id == project.id
    ).sort(ChatMessage.created_at).to_list()
    
    return chat_messages