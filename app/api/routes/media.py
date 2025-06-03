from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from .auth import get_current_user
from app.models import Scene_model

router = APIRouter(prefix="/media", tags=["Media"],dependencies=[Depends(get_current_user)] )



@router.get("/get_scene_video/{scene_id}")
async def get_video(scene_id: PydanticObjectId):
    
    scene = await Scene_model.get(scene_id)
    
    video_path = scene.video_path
    if video_path.exists():
       return FileResponse(media_type="video/mp4", path=video_path,filename=f'{scene.scene_name}')
    return {"error": "video not found"}