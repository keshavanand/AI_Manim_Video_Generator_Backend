import asyncio
import nest_asyncio
from pathlib import Path
import subprocess
import os
from beanie import PydanticObjectId
from slugify import slugify
from app.core.celery_app import celery
from app.models.models import Media, Scene as Scene_model, Project as Project_model
from app.core.logging_config import logger
from app.models import Status
from app.core import settings
from app.db.base import init_beanie_db

# create folders and update project_path
def create_folder_for_project(id: PydanticObjectId, title: str) -> str:
    try:
        slug = slugify(title)
        folder_name = f"{slug}-{id}"
        path = os.path.join(settings.MANIM_PROJECTS, folder_name)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created folder for project: {path}")
        return path
    except Exception as e:
        logger.error(f"Error creating folder for project '{title}' (id: {id}): {e}")
        raise

# initialize manim files for current project
def create_manim_project(title: str, path: Path) -> str:
    try:
        title_slug = slugify(title)
        full_path = os.path.join(path, title)
        cmd = f'python -m manim init project "{full_path}" --default'
        logger.info(f"Running command to initialize manim project: {cmd}")

        process = subprocess.run(
            cmd,
            shell=True,
            text=True,
            input="Default",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            logger.error(f"Manim init failed for {title_slug} at {full_path}: {process.stderr}")
            raise RuntimeError(f"Manim init failed: {process.stderr}")
        else:
            logger.info(f"Created Manim project for {title_slug} at {full_path}")
            logger.debug(f"Manim init output: {process.stdout}")
        return full_path
    except Exception as e:
        logger.error(f"Error creating Manim project for {title}: {e}")
        raise

# recreate project and scenes files if deleted before running 
async def checkProjectFiles(scene_id: PydanticObjectId):
    # check if project exist
    # if not intialize manim project with same project name and id
    scene: Scene_model = await Scene_model.get(scene_id)
    await scene.fetch_link("project")
    project = scene.project
    if not os.path.isdir(project.manim_path):
        create_folder_for_project(scene.project, project.title)
        create_manim_project(project.title, project.project_path)

    # check if scene file exist
    # update code if no scene file create fresh
    if not os.path.exists(scene.scene_path):
        file_path = Path(scene.scene_path).parent
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(scene.scene_path, "w", encoding="utf-8") as f:
            f.write(scene.scene_code)

    # update previous files with new content

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

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    
@celery.task
def run_manim_task(file_path, scene_id, media_id, file_name):
    async def update_scene_and_media():
        await init_beanie_db()

        # Make sure project files are valid first
        await checkProjectFiles(scene_id)

        scene = await Scene_model.get(scene_id)
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