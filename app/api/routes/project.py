from datetime import datetime
from pathlib import Path
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import Project, CreateProject, ProjectPrompt, UpdateProject
from app.schemas.llm_response import LLMResponse
from app.services import (
    generate_code, generate_manim_file, edit_manim, run_manim,
    create_seperate_scenes, parse_gemini_response, BASE_PROMPT,
    create_folder_for_project, create_manim_project, create_db_entries,
    systemPrompt, BASE_PROMPT, apply_bolt_artifact, initialize_project,
    editSystemPrompt, merge_llm_response
)
from app.core import settings
from typing import Annotated, List

from app.services.llm_client import generate_code_new
from .auth import get_current_user
from app.models import User as User_model, Project as Project_model,Scene as Scene_model
router = APIRouter(
    prefix="/project",
    tags=["Project"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/create_new_Project", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_newProject(
    cp: CreateProject,
    current_user: Annotated[User_model, Depends(get_current_user)],
)->Project:
    # if project already exist and user is editing it
    if cp.id:
        print("Editing existing project")
        project = await Project_model.get(cp.id)
        previous_files: LLMResponse = project.previous_files

        code_response = generate_code_new(cp.prompt, BASE_PROMPT, editSystemPrompt("", previous_files))
        parsed = code_response.parsed
        print(f"Response:{parsed}")
        await apply_bolt_artifact(parsed, project, project.manim_path, current_user)

        updated_files = merge_llm_response(previous_files, parsed)
        project.previous_files = updated_files
        await project.save()

        return project

    # For new projects
    print("Creating new project")
    code_response= generate_code_new(cp.prompt, BASE_PROMPT,systemPrompt(""))
    parsed: LLMResponse = code_response.parsed
    
    project = await initialize_project(cp, current_user, cp.id, parsed)
    project.previous_files = parsed
    await project.save()

    return project

@router.post("/create_project", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(
    project: CreateProject,
    current_user: Annotated[User_model, Depends(get_current_user)]
) -> Project:
    # Generate scenes from LLM
    prompt = f"{BASE_PROMPT}---This is user prompt:{project.prompt}---"
    code_response = generate_code(prompt).text
    scenes_list = parse_gemini_response(code_response)

    # Save and prepare files
    generate_manim_file(settings.SCENES_PATH, code_response)
    edit_manim(settings.SCENES_PATH)
    create_seperate_scenes(scenes_list)

    # Create project in DB
    new_project = Project_model(
        title=f"Project-{project.prompt}",
        description=project.description,
        original_prompt=project.prompt,
        project_path=str(settings.MANIM_PATH),
        owner=current_user
    )
    await new_project.create()

    # Create scene instances in DB
    for scene in scenes_list:
        output = run_manim(settings.SCENES_FOLDER, scene_name=scene["scene_name"])
        scene["output"] = output
        a_scene = Scene_model(
            scene_name=scene.get("scene_name"),
            scene_code=scene.get("code"),
            video_path=str(Path(settings.VIDEO_PATH) / scene.get("scene_name", "scene") / "480p15" / f"{scene.get('scene_name', 'scene')}.mp4"),
            scene_path=str(Path(settings.SCENES_FOLDER) / scene.get("scene_name", "scene")),
            owner=current_user,
            project=new_project,
            scene_output=output,
            scene_prompt=project.prompt
        )
        await a_scene.create()

    return new_project.model_dump()

@router.get("/get_projects", response_model=List[Project])
async def get_projects(current_user: Annotated[User_model, Depends(get_current_user)]):
    projects = await Project_model.find(
        Project_model.owner.id == current_user.id,
        fetch_links=False
    ).to_list()
    return projects

@router.put("/update_project/{id}", response_model=Project)
async def update_project(id: PydanticObjectId, req: UpdateProject):
    req_dict = {k: v for k, v in req.model_dump().items() if v is not None}
    if not req_dict:
        raise HTTPException(status_code=400, detail="No fields to update.")
    req_dict['updated_at'] = datetime.utcnow()
    project = await Project_model.get(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await project.update({"$set": req_dict})
    return project

@router.delete("/delete_project/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: PydanticObjectId):
    project = await Project_model.get(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await Scene_model.find(Scene_model.project.id == project.id).delete_many()
    await project.delete()
    return {"detail": "Project deleted"}