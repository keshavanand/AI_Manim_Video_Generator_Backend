
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.core import get_current_user
from app.models import ChatMessage, User as User_model, Project as Project_model
from app.core.logging_config import logger

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
    try:
        logger.info(f"Fetching chat history for project: {id}")
        project = await Project_model.get(id)
        if not project:
            logger.error(f"Project not found: {id}")
            raise HTTPException(status_code=404, detail="Project not found")
        # Fetch chat messages for the current user
        chat_messages = await ChatMessage.find(
            ChatMessage.project.id == project.id
        ).sort(ChatMessage.created_at).to_list()
        logger.info(f"Found {len(chat_messages)} chat messages for project: {id}")
        return chat_messages
    except Exception as e:
        logger.error(f"Error fetching chat history for project {id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching chat history")
