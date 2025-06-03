from pathlib import Path
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from app.services import generate_code
from app.core import settings
from app.services import run_manim,  update_scene, edit_scene, parse_single_scene,create_single_scene
from app.services import  RE_BASE_PROMPT, SCENE_PROMPT
from app.schemas import Re_prompt, UpdateScene, SceneSchema
from typing import Annotated
from .auth import get_current_user
from app.models import  User_model, Project_model, Scene_model

router = APIRouter(prefix="/scene", tags=["Scene"],dependencies=[Depends(get_current_user)] )

@router.post("/re-prompt")
async def re_prompt(body: Re_prompt):
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


@router.get("/get_scenes")
async def get_scenes(projectID: PydanticObjectId):

    scenes = await Scene_model.find(
        Scene_model.project.id == projectID
    ).to_list()

    return scenes

@router.delete("/delete_scene")
async def delete_scene(id: PydanticObjectId):
    scene = await Scene_model.get(id)
    await scene.delete()
    return "Scene Deleted"

@router.put("/update_scene/{id}")
async def update_scene(id: PydanticObjectId, req: UpdateScene):
    req = {k:v for k,v in req.model_dump().items() if v is not None}
    update_query = {
        "$set": {f: v for f,v in req.items()}
    }

    scene = await Scene_model.get(id)
    await scene.update(update_query)
    return "scene updated"

@router.post("/add_scene_with_prompt")
async def add_scene_with_prompt(req: SceneSchema, currentUser: Annotated[User_model, Depends(get_current_user)]):
    generated_scene = generate_code(SCENE_PROMPT + "Original User Prompt:" + req.scene_prompt).text
    generated_scene = parse_single_scene(generated_scene)

    create_single_scene(generated_scene)
    output = run_manim(settings.SCENES_FOLDER,scene_name=generated_scene["scene_name"])
    print(f"Successfully runned scene: {generated_scene["scene_name"]}")

    project = await Project_model.get(req.project_id)

    scene = Scene_model(
        scene_name=generated_scene["scene_name"],
        scene_code=generated_scene["code"],
        scene_output=output,
        scene_prompt=req.scene_prompt,
        video_path=Path(settings.VIDEO_PATH) / generated_scene.get("scene_name", "scene") / "480p15" / f"{generated_scene.get("scene_name", "scene")}.mp4",
        scene_path=Path(settings.SCENES_FOLDER)/generated_scene.get("scene_name", "scene"),
        owner=currentUser,
        project=project
    )

    await scene.create()
    print(f"Scene{scene.scene_name} added to db")