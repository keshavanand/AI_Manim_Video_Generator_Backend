# Routes for LLM code input, editing, scene management
from pathlib import Path
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException,status
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes, parse_gemini_response, update_scene, edit_scene
from fastapi.responses import FileResponse
from app.services import BASE_PROMPT, RE_BASE_PROMPT
from app.schemas import Re_prompt, User_Data
from typing import Annotated
from .auth import get_current_user
from app.models import  User_model, Project_model, Scene_model


router = APIRouter(prefix="/manim", tags=["Manim"])

@router.post("/generate/{prompt}")
async def generate(prompt: str, currentUser: Annotated[User_model, Depends(get_current_user)]) -> list:
    
    code = generate_code(f'{BASE_PROMPT}---This is user prompt:{prompt}---').text # get repsone in string from LLM
    scenes_list = parse_gemini_response(code) # parse the response

    generate_manim_file(settings.SCENES_PATH,code)
    edit_manim(settings.SCENES_PATH)
    create_seperate_scenes(scenes_list)

    project = Project_model(title=f"Project-{prompt}", 
                            description=prompt, 
                            original_prompt=f'{BASE_PROMPT}---This is user prompt:{prompt}---',
                            project_path=Path(settings.MANIM_PATH),
                            owner=currentUser)
    await project.create()
    print(f"Project {project.title} created")

    
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
                              project=project,
                              scene_output=output,
                              scene_prompt=prompt)    
        await a_scene.create()
        print(f"Scene{a_scene.scene_name} added to db")

    return scenes_list

@router.get("/get_scene_video/{scene_id}")
async def get_video(scene_id: PydanticObjectId, current_user: Annotated[User_model, Depends(get_current_user)]):
    
    scene = await Scene_model.get(scene_id, fetch_links=True)
    if not scene.owner.id == current_user.id:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unauthorized Access",
        )
    
    video_path = scene.video_path
    if video_path.exists():
       return FileResponse(media_type="video/mp4", path=video_path,filename=f'{scene.scene_name}')
    return {"error": "video not found"}

@router.post("/re-prompt")
async def re_prompt(body: Re_prompt, currentUser: Annotated[User_model, Depends(get_current_user)]):
    scene = await Scene_model.get(body.scene_Id)
    code = generate_code(RE_BASE_PROMPT.format(original_prompt="demo nerual network",
                                               scene_name=scene.scene_name,
                                               scene_code=scene.scene_code,
                                               scene_output=scene.scene_output,
                                               prompt=body.prompt)).text
    
    update_scene(scene.scene_name,code)
    edit_scene(settings.MANIM_PATH/Path("scenes/"+scene.scene_name+".py"))
    output = run_manim(settings.SCENES_FOLDER,scene_name=scene.scene_name)
    print(f"Successfully runned scene: {scene.scene_name}")

    scene.scene_output = output
    await scene.save()

    return {"success":f"scene {scene.scene_name} updated"}

@router.get("/get_projects")
async def get_projects(currentUser: Annotated[User_model, Depends(get_current_user)]):
    
    projects = await Project_model.find(
        Project_model.owner.id == currentUser.id,
        fetch_links= False
    ).to_list()

    return projects

@router.get("/get_scenes")
async def get_scenes(projectID: PydanticObjectId,currentUser: Annotated[User_model, Depends(get_current_user)]):

    scenes = await Scene_model.find(
        Scene_model.project.id == projectID
    ).to_list()

    return scenes