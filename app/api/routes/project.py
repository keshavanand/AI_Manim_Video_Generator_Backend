from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import Project, Prompt, UpdateProject
from app.schemas.llm_response import LLMResponse
from app.services import (
    BASE_PROMPT, systemPrompt, editSystemPrompt, merge_llm_response,
    initialize_project, apply_bolt_artifact
)
from typing import Annotated, List
from app.services.llm_client import generate_code_new
from .auth import get_current_user
from app.models import User as User_model, Project as Project_model, Scene as Scene_model, ChatMessage, ChatRole, Media
from app.core.logging_config import logger
import os
import shutil

router = APIRouter(
    prefix="/project",
    tags=["Project"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/create_project", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(prompt: Prompt, current_user: Annotated[User_model, Depends(get_current_user)]) -> Project:
    try:
        logger.info("Creating new project")
        code_response = generate_code_new(prompt.prompt, BASE_PROMPT, systemPrompt(""))
        parsed: LLMResponse = code_response.parsed
        logger.debug(f"LLM Response for new project: {parsed}")

        project = await initialize_project(prompt, current_user, parsed)
        if not project:
            logger.error("Failed to initialize project")
            raise HTTPException(status_code=500, detail="Failed to initialize project")
        project.previous_files = parsed
        await project.save()

        # add chat message for the llm response
        chat_message = ChatMessage(
            role=ChatRole.assistant,
            content=parsed.message,
            project=project)
        await chat_message.create()

        logger.info("New project created and saved: %s", project.id)
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail="Error creating project")


@router.post("/edit_project", status_code=status.HTTP_201_CREATED, response_model=Project)
async def edit_project(prompt: Prompt, current_user: Annotated[User_model, Depends(get_current_user)]) -> Project:
    try:
        logger.info("Editing existing project with id: %s", prompt.id)
        project = await Project_model.get(prompt.id)
        if not project:
            logger.error(f"Project not found: {prompt.id}")
            raise HTTPException(status_code=404, detail="Project not found")
        previous_files: LLMResponse = project.previous_files

        # create chat message for the project
        chat_message = ChatMessage(
            role=ChatRole.user,
            content=prompt.prompt,
            project=project)
        await chat_message.create()

        code_response = generate_code_new(prompt.prompt, BASE_PROMPT, editSystemPrompt("", previous_files))
        parsed = code_response.parsed
        logger.debug(f"LLM Response for edit: {parsed}")
        await apply_bolt_artifact(parsed, project, project.manim_path, current_user)

        updated_files = merge_llm_response(previous_files, parsed)
        project.previous_files = updated_files
        await project.save()

        # add chat message for the llm response
        chat_message = ChatMessage(
            role=ChatRole.assistant,
            content=parsed.message,
            project=project)
        await chat_message.create()

        logger.info("Project edited and saved: %s", project.id)
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing project {prompt.id}: {e}")
        raise HTTPException(status_code=500, detail="Error editing project")



@router.get("/get_projects", response_model=List[Project])
async def get_projects(current_user: Annotated[User_model, Depends(get_current_user)]):
    try:
        logger.info("Fetching projects for user: %s", current_user.id)
        projects = await Project_model.find(
            Project_model.owner.id == current_user.id,
            fetch_links=False
        ).to_list()
        logger.debug("Found %d projects for user %s", len(projects), current_user.id)
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching projects")


@router.put("/update_project/{id}", response_model=Project)
async def update_project(id: PydanticObjectId, req: UpdateProject):
    try:
        logger.info("Updating project: %s", id)
        req_dict = {k: v for k, v in req.model_dump().items() if v is not None}
        if not req_dict:
            logger.warning("No fields to update for project: %s", id)
            raise HTTPException(status_code=400, detail="No fields to update.")
        req_dict['updated_at'] = datetime.utcnow()
        project = await Project_model.get(id)
        if not project:
            logger.error("Project not found: %s", id)
            raise HTTPException(status_code=404, detail="Project not found")
        await project.update({"$set": req_dict})
        logger.info("Project updated: %s", id)
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating project")



@router.delete("/delete_project/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: PydanticObjectId):
    try:
        logger.info("Deleting project: %s", id)
        project = await Project_model.get(id)
        if not project:
            logger.error("Project not found for deletion: %s", id)
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete related scenes
        try:
            await Scene_model.find(Scene_model.project.id == project.id).delete_many()
        except Exception as e:
            logger.warning(f"No related scenes or error deleting scenes for project {id}: {e}")

        # Delete related media
        try:
            media = await Media.find_many(Media.projects.id == project.id).to_list()
            for m in media:
                if(os.path.isdir(m.path)):
                    shutil.rmtree(m.path)
                    await m.delete()
        except Exception as e:
            logger.warning(f"No related media or error deleting media for project {id}: {e}")

        # Delete related chat messages
        try:
            await ChatMessage.find(ChatMessage.project.id == project.id).delete_many()
        except Exception as e:
            logger.warning(f"No related chat messages or error deleting chat messages for project {id}: {e}")

        if (os.path.isdir(project.project_path)):
            shutil.rmtree(project.project_path)
        await project.delete()
        logger.info("Project and its associated scenes, media, and files deleted: %s", id)
        return {"detail": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting project")
