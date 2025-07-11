
import os
from pathlib import Path
from typing import List
from beanie import PydanticObjectId
from slugify import slugify
from app.core import settings
import subprocess
from app.models import User as User_model, Project as Project_model,Scene as Scene_model, ProjectStatus, ChatMessage, ChatRole, Status, Media, MediaType
from beanie import Document
import re
from app.schemas.llm_response import LLMResponse
from app.core.logging_config import logger

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
        full_path = str(path) + "\\" + title_slug
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


# create initial db entries
async def create_db_entries(prompt: str, user: User_model, title: str) -> List[Document]:
    try:
        project = Project_model(
            title=title,
            owner=user,
            status=ProjectStatus.queued
        )
        await project.create()
        logger.info(f"Created project DB entry: {project.id}")

        chat = ChatMessage(
            role=ChatRole.user,
            content=prompt,
            project=project
        )
        await chat.create()
        logger.info(f"Created initial chat message for project: {project.id}")

        return [project, chat]
    except Exception as e:
        logger.error(f"Error creating initial DB entries for project '{title}': {e}")
        raise


async def initialize_project(prompt, current_user, data):
    try:
        title = data.title
        logger.info(f"Initializing project with title: {title}")

        project_result = await create_db_entries(prompt.prompt, current_user, title)
        if not project_result or not isinstance(project_result, list) or not project_result[0]:
            logger.error("Failed to create initial DB entries for project.")
            return None
        project: Project_model = project_result[0]

        try:
            project_path = create_folder_for_project(project.id, project.title)
        except Exception as e:
            logger.error(f"Failed to create project folder for project: {project.id}, error: {e}")
            return None
        project.project_path = project_path

        try:
            manim_path = create_manim_project(project.title, project_path)
            project.status = ProjectStatus.complete
        except Exception as e:
            logger.error(f"Failed to create manim project for project: {project.id}, error: {e}")
            return None
        project.manim_path = manim_path
        await project.save()

        # Create/update file content from llm response
        try:
            await apply_bolt_artifact(data, project, manim_path, current_user)
        except Exception as e:
            logger.error(f"Error in apply_bolt_artifact: {e}")
            return None

        logger.info(f"Project initialized successfully: {project.id}")
        return project
    except Exception as e:
        logger.error(f"Error initializing project: {e}")
        return None


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
    

async def apply_bolt_artifact(data, project, manim_path, current_user):
    try:
        # Update project title
        project.title = data.title

        # Handle files
        for file_entry in data.files:
            file_path = os.path.join(manim_path, file_entry.filePath)
            status = file_entry.status
            content = file_entry.content

            scene = await Scene_model.find_one(
                Scene_model.project.id == project.id,
                Scene_model.scene_name == file_entry.scene_name
            )

            if not scene:
                scene = Scene_model(
                    scene_name=file_entry.scene_name,
                    scene_code=content,
                    status=Status.pending,
                    scene_path=file_path,
                    owner=current_user,
                    project=project
                )
                await scene.create()
                logger.info(f"Created new scene in DB: {file_entry.scene_name}")
            
            media = await Media.find_one(
                Media.projects.id == project.id,
                Media.scene.id == scene.id
            )

            if not media:

                media = Media(
                        type=MediaType.video,
                        projects=project,
                        scene=scene,
                        status=Status.pending
                    )
                await media.create()
                logger.info(f"Created new media in DB for: {file_entry.scene_name}")


            if status == "deleted":
                logger.info(f"🗑️ Deleting {file_path}")
                await scene.delete()
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")
            else:
                logger.info(f"💾 Writing to {file_path} (status: {status})")
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(f"Wrote content to {file_path}")
                except Exception as e:
                    logger.error(f"Error writing to file {file_path}: {e}")
                    continue
                logger.info("Running code")
                output, status = run_manim(file_path, file_entry.scene_name)
                if status and status == "success":
                    scene.status = Status.ready
                    media.status = Status.ready
                    media.path = str(Path(settings.VIDEO_PATH) / file_entry.file_name / "480p15" / f"{scene.scene_name}.mp4")
                else:
                    scene.status = Status.error
                    media.status = Status.error
                scene.scene_output = output
                await scene.save()
                await media.save()
                logger.info(f"Updated scene output and video path for: {scene.scene_name}")

        # Handle commands
        for command in data.commands:
            logger.info(f"🚀 Shell Command: {command}")
            # Optionally run command
            #run_manim()

    except Exception as e:
        logger.error(f"❌ Error while parsing response: {e}")

    
def merge_llm_response(previous: LLMResponse, updates: LLMResponse) -> LLMResponse:
    if not updates:
        return previous
    
    updated_files = updates.files
    updated_map = {f.file_name:  f for f in updated_files}

    merged_files = []
    seen = set()

    # Keep existing ones unless deleted or updated
    for file in previous.files:
        fname = file.file_name
        if fname in updated_map:
            update = updated_map[fname]
            seen.add(fname)
            if update.status == "deleted":
                continue
            else:
                merged_files.append(update) #updated
        else:
            merged_files.append(file) # unchanged

    # Add any new files that weren’t in the original list
    for fname, update in updated_map.items():
        if fname not in seen and update.status == "created":
            merged_files.append(update)

    return LLMResponse(
        id=previous.id,
        title=previous.title,
        files=merged_files,
        commands=updates.commands # Optional: merge/append instead if needed
    )


def updateSceneFile(path:str, code:str):
    logger.info(f"💾 Writing to {path} (status: updating)")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        logger.info(f"Wrote content to {path}")
    except Exception as e:
        logger.error(f"Error writing to file {path}: {e}")