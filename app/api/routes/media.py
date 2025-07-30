
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from .auth import get_current_user
from app.models import Media
from pathlib import Path
from app.core.logging_config import logger

router = APIRouter(
    prefix="/media",
    tags=["Media"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/get_scene_video/{scene_id}")
async def get_video(scene_id: PydanticObjectId):
    try:
        logger.info(f"Fetching video for scene: {scene_id}")
        media = await Media.find_one(
            Media.scene.id == scene_id
        )
        if media.status == "error":
            logger.error(f"Scene did not rendered has some errors see output for details")
            raise HTTPException(status_code=404, detail="Scene Error")
        if not media or not media.path:
            logger.error(f"Video not found for scene: {scene_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        video_path = Path(media.path)
        if not video_path.exists():
            logger.error(f"Video file does not exist: {video_path}")
            raise HTTPException(status_code=404, detail="Video file does not exist")
        logger.info(f"Returning video file: {video_path}")
        return FileResponse(
            media_type="video/mp4",
            path=str(video_path),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video for scene {scene_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching video")
