
from pathlib import Path
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.scene import AddSceneSchema
from app.services import (
    generate_code, run_manim, update_scene, edit_scene, updateSceneFile,
    parse_single_scene, create_single_scene, RE_BASE_PROMPT, SCENE_PROMPT,
)
from app.core import settings
from app.schemas import RePrompt, UpdateScene, SceneSchema
from typing import Annotated, List
from .auth import get_current_user
from app.models import User as User_model, Project as Project_model,Scene as Scene_model, Media, Status
from app.core.logging_config import logger

router = APIRouter(
    prefix="/scene",
    tags=["Scene"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/re-prompt")
async def re_prompt(body: RePrompt):
    try:
        logger.info(f"Re-prompting scene: {body.scene_Id}")
        scene = await Scene_model.get(body.scene_Id)
        if not scene:
            logger.error(f"Scene not found: {body.scene_Id}")
            raise HTTPException(status_code=404, detail="Scene not found")
        code = generate_code(RE_BASE_PROMPT.format(
            original_prompt=scene.scene_prompt,
            scene_name=scene.scene_name,
            scene_code=scene.scene_code,
            scene_output=scene.scene_output,
            prompt=body.prompt
        )).text

        update_scene(scene.scene_name, code)
        edit_scene(settings.MANIM_PATH / Path("scenes/" + scene.scene_name + ".py"))
        output = run_manim(settings.SCENES_FOLDER, scene_name=scene.scene_name)

        scene.scene_output = output
        await scene.save()
        logger.info(f"Scene {scene.scene_name} updated successfully")
        return {"success": f"scene {scene.scene_name} updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in re-prompt for scene {body.scene_Id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating scene")


@router.get("/get_scenes", response_model=List[SceneSchema])
async def get_scenes(projectID: PydanticObjectId):
    try:
        logger.info(f"Fetching scenes for project: {projectID}")
        scenes = await Scene_model.find(
            Scene_model.project.id == projectID,
            fetch_links=False
        ).to_list()
        logger.info(f"Found {len(scenes)} scenes for project: {projectID}")
        return scenes
    except Exception as e:
        logger.error(f"Error fetching scenes for project {projectID}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching scenes")


@router.delete("/delete_scene/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scene(id: PydanticObjectId):
    try:
        logger.info(f"Deleting scene: {id}")
        scene = await Scene_model.get(id)
        await Media.find_one(Media.scene.id == id).delete_one()
        if not scene:
            logger.error(f"Scene not found: {id}")
            raise HTTPException(status_code=404, detail="Scene not found")
        await scene.delete()
        logger.info(f"Scene deleted: {id}")
        return {"detail": "Scene deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scene {id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting scene")


@router.put("/update_scene/{id}")
async def update_scene_api(id: PydanticObjectId, req: UpdateScene):
    try:
        logger.info(f"Updating scene: {id}")
        req_dict = {k: v for k, v in req.model_dump().items() if v is not None}
        if not req_dict:
            logger.warning(f"No fields to update for scene: {id}")
            raise HTTPException(status_code=400, detail="No fields to update.")
        scene = await Scene_model.get(id)
        if not scene:
            logger.error(f"Scene not found: {id}")
            raise HTTPException(status_code=404, detail="Scene not found")
        await scene.update({"$set": req_dict})
        logger.info(f"Scene updated: {id}")
        return {"detail": "Scene updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scene {id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating scene")


@router.post("/add_scene_with_prompt", response_model=SceneSchema)
async def add_scene_with_prompt(
    req: AddSceneSchema,
    current_user: Annotated[User_model, Depends(get_current_user)]
):
    try:
        logger.info(f"Adding scene with prompt for project: {req.project_id}")
        generated_scene = generate_code(
            SCENE_PROMPT + "Original User Prompt:" + req.scene_prompt
        ).text
        generated_scene = parse_single_scene(generated_scene)

        create_single_scene(generated_scene)
        output = run_manim(settings.SCENES_FOLDER, scene_name=generated_scene["scene_name"])

        project = await Project_model.get(req.project_id)
        if not project:
            logger.error(f"Project not found: {req.project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        scene = Scene_model(
            scene_name=generated_scene["scene_name"],
            scene_code=generated_scene["code"],
            scene_output=output,
            scene_prompt=req.scene_prompt,
            video_path=str(Path(settings.VIDEO_PATH) / generated_scene.get("scene_name", "scene") / "480p15" / f"{generated_scene.get('scene_name', 'scene')}.mp4"),
            scene_path=str(Path(settings.SCENES_FOLDER) / generated_scene.get("scene_name", "scene")),
            owner=current_user,
            project=project
        )

        await scene.create()
        logger.info(f"Scene created: {scene.scene_name} for project: {req.project_id}")
        return scene
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding scene with prompt for project {req.project_id}: {e}")
        raise HTTPException(status_code=500, detail="Error adding scene")
    
@router.post("/run_scene/{scene_id}", )
async def run_scene(scene_id: PydanticObjectId):
    try:
        logger.info("Fetching scene")
        scene:Scene_model = await Scene_model.get(scene_id)
        if not scene:
            raise HTTPException(status_code=404, detail="No scene found")

        logger.info(f"Updating scene code:{scene.scene_name}")
        updateSceneFile(scene.scene_path,scene.scene_code)

        logger.info(f"Running scene:{scene.scene_name}")
        output, status = run_manim(scene.scene_path, scene.scene_name)
        scene.scene_output = output
        if status=="success":
            scene.status = Status.ready
        scene.status = Status.error
        await scene.save()
        return {"detail": "Scene succesfully runned"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error while runing scene")
        raise HTTPException(status_code=500, detail="Error running scene")
