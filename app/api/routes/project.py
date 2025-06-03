
from pathlib import Path
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes, parse_gemini_response
from app.services import BASE_PROMPT
from app.schemas import  UpdateProject, CreateProject
from typing import Annotated
from .auth import get_current_user
from app.models import  User_model, Project_model, Scene_model

router = APIRouter(prefix="/project", tags=["Project"],dependencies=[Depends(get_current_user)] )

@router.post("/create_project", status_code=201)
async def generate(project: CreateProject, currentUser: Annotated[User_model, Depends(get_current_user)]) -> list:
    
    code = generate_code(f'{BASE_PROMPT}---This is user prompt:{project.prompt}---').text # get repsone in string from LLM
    scenes_list = parse_gemini_response(code) # parse the response

    generate_manim_file(settings.SCENES_PATH,code)
    edit_manim(settings.SCENES_PATH)
    create_seperate_scenes(scenes_list)

    new_project = Project_model(title=f"Project-{project.title}", 
                            description=project.description, 
                            original_prompt=f'{BASE_PROMPT}---This is user prompt:{project.prompt}---',
                            project_path=Path(settings.MANIM_PATH),
                            owner=currentUser)
    await new_project.create()
    print(f"Project {new_project.title} created")

    
    # create scene instanse for each scene and store it in db
    for scene in scenes_list:
        output = run_manim(settings.SCENES_FOLDER,scene_name=scene["scene_name"])
        print(f"Successfully runned scene: {scene["scene_name"]}")
        scene["ouptut"] = output

        a_scene = Scene_model(scene_name=scene.get("scene_name", None),
                              scene_code=scene.get("code", None),
                              video_path=Path(settings.VIDEO_PATH) / scene.get("scene_name", "scene") / "480p15" / f"{scene.get("scene_name", "scene")}.mp4",
                              scene_path=Path(settings.SCENES_FOLDER)/scene.get("scene_name", "scene"),
                              owner=currentUser,
                              project=new_project,
                              scene_output=output,
                              scene_prompt=project.prompt)    
        await a_scene.create()
        print(f"Scene{a_scene.scene_name} added to db")

    return scenes_list

@router.get("/get_projects")
async def get_projects(currentUser: Annotated[User_model, Depends(get_current_user)]):
    
    projects = await Project_model.find(
        Project_model.owner.id == currentUser.id,
        fetch_links= False
    ).to_list()

    return projects

@router.put("/update_project",response_model=UpdateProject)
async def update_project(id: PydanticObjectId, req: UpdateProject):
    req = {k: v for k,v in req.model_dump().items() if v is not None}
    update_query = {"$set":{
        field: value for field, value in req.items()
        }
    }
    project = await Project_model.get(id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )   
    await project.update(update_query)
    return project

@router.delete("/delete_project/{id}")
async def delete_project(id: PydanticObjectId):
    project = await Project_model.get(id)
    scenes = await Scene_model.find(
        Scene_model.project.id == project.id
    ).delete_many()

    await project.delete()

    return "Project deleted"