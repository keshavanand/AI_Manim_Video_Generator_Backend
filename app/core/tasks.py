import asyncio
from pathlib import Path
import subprocess
from app.core.celery_app import celery
from app.models.models import Media, Scene
from app.core.logging_config import logger
from app.models import Status
from app.core import settings
from app.db.base import init_beanie_db

def run_manim(path: Path, scene_name: str) -> list[str]:
    """Run Manim CLI for a given scene file and return output or error."""
    import os
    try:
        cmd = f'python -m manim -ql --disable_caching "{path}" "{scene_name}"'
        logger.info(f"Running Manim CLI: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True  # captures both stdout and stderr
        )

        if result.returncode == 0:
            logger.info(f"Manim ran successfully for scene: {scene_name}")
            logger.debug(f"Manim output: {result.stdout}")
            return [result.stdout, "success"]
        else:
            error_msg = f"[❌ Manim Error] Scene: {scene_name}\n{result.stderr}"
            logger.error(error_msg)
            return [error_msg, "error"]

    except Exception as e:
        fallback_error = f"[⚠️ Subprocess Exception] {scene_name}: {str(e)}"
        logger.error(fallback_error)
        return fallback_error

@celery.task
def run_manim_task(file_path, scene_id, media_id, file_name):
    async def update_scene_and_media():
        await init_beanie_db()
        scene = await Scene.get(scene_id)
        media = await Media.get(media_id)
        output, status = run_manim(file_path, scene.scene_name)
        if status and status == "success":
            scene.status = Status.ready
            media.status = Status.ready
            media.path = str(Path(settings.VIDEO_PATH) / file_name / "480p15" / f"{scene.scene_name}.mp4")
        else:
            scene.status = Status.error
            media.status = Status.error
        scene.scene_output = output
        await scene.save()
        await media.save()
        logger.info(f"Updated scene output and video path for: {scene.scene_name}")

    asyncio.run(update_scene_and_media())
    return None