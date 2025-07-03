import os
from pathlib import Path
from typing import List
from beanie import PydanticObjectId
from slugify import slugify
from app.core import settings
import subprocess
from app.models import User as User_model, Project as Project_model,Scene as Scene_model, ProjectStatus, ChatMessage, ChatRole, Status
from beanie import Document
import re
from app.schemas.llm_response import LLMResponse
    
# create foleders and update project_path
def create_folder_for_project(id: PydanticObjectId, title: str)->str:
    slug = slugify(title)
    folder_name = f"{slug}-{id}"
    path = os.path.join(settings.MANIM_PROJECTS, folder_name)
    os.makedirs(path, exist_ok=True)
    return path
   
# intialize manim files for current project
def create_manim_project(title:str,path:Path)->str:
    try:
        title = slugify(title)
        full_path = path + "\\" + title
        cmd=f'python -m manim init project {full_path} --default'

        process = subprocess.run(
            cmd,
            shell=True,
            text=True,
            input="Default",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) 

        print(process.stdout)
        if process.stderr:
            print("Errors:", process.stderr)

        print(f"Created Manim project for {title} at {path}")
        return full_path
    except Exception as e:
        print(f"Error creatin Manim projec for {title}: {e}")

# create intial db entries
async def create_db_entries(prompt: str, user: User_model, title: str)->List[Document]:

    project = Project_model(
        title=title,
        description=prompt,
        original_prompt=prompt,
        owner=user
    )
    await project.create()

    chat = ChatMessage(
        role=ChatRole.user,
        content=prompt,
        project=project
    )
    
    await chat.create()

    return [project, chat]

async def initialize_project(prompt,current_user, projecet_id, data):
    title = data.title

    project, chat = await create_db_entries(prompt.prompt, current_user, title)
    project_path = create_folder_for_project(project.id, project.title)
    project.project_path = project_path

    manim_path = create_manim_project(project.title, project_path)

    project.manim_path = manim_path
    await project.save()

    # Create/update file content from llm response
    await apply_bolt_artifact(data, project, manim_path,current_user)

    return project


def run_manim(path: Path, scene_name: str) -> str:
    """Run Manim CLI for a given scene file and return output or error."""
    try:
        cmd = f'python -m manim -ql "{path}" "{scene_name}"'
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True  # captures both stdout and stderr
        )

        if result.returncode == 0:
            return result.stdout
        else:
            error_msg = f"[❌ Manim Error] Scene: {scene_name}\n{result.stderr}"
            print(error_msg)
            return error_msg

    except Exception as e:
        fallback_error = f"[⚠️ Subprocess Exception] {scene_name}: {str(e)}"
        print(fallback_error)
        return fallback_error
    
async def apply_bolt_artifact(data, project, manim_path,current_user):
    try:
        # Update project title
        project.title = data.title

        # Handle files
        for file_entry in data.files:
            file_path = os.path.join(manim_path, file_entry.filePath)
            status = file_entry.status
            content = file_entry.content


            scene = await Scene_model.find_one(
                Scene_model.project.id==project.id, 
                Scene_model.scene_name==file_entry.scene_name
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

            if status == "deleted":
                print(f"🗑️ Deleting {file_path}")
                await scene.delete()
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                print(f"💾 Writing to {file_path} (status: {status})")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("Running code")
                output = run_manim(file_path,file_entry.scene_name)
                scene.scene_output = output
                scene.video_path = str(Path(settings.VIDEO_PATH) / file_entry.file_name / "480p15" / f"{scene.scene_name}.mp4")
                await scene.save()

        # Handle commands
        for command in data.commands:
            print(f"🚀 Shell Command: {command}")
            # Optionally run command
            #run_manim()

    except Exception as e:
        print(f"❌ Error while parsing response: {e}")

    
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
