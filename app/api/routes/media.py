from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from .auth import get_current_user
from app.models import Scene as Scene_model
from pathlib import Path

router = APIRouter(
    prefix="/media",
    tags=["Media"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/get_scene_video/{scene_id}")
async def get_video(scene_id: PydanticObjectId):
    scene = await Scene_model.get(scene_id)
    if not scene or not scene.video_path:
        raise HTTPException(status_code=404, detail="Video not found")
    video_path = Path(scene.video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file does not exist")
    return FileResponse(
        media_type="video/mp4",
        path=str(video_path),
        filename=f"{scene.scene_name}.mp4"
    )