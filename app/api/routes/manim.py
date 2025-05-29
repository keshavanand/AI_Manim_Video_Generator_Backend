# Routes for LLM code input, editing, scene management
from pathlib import Path
from fastapi import APIRouter, Depends
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes, parse_gemini_response, update_scene, edit_scene
from fastapi.responses import FileResponse
from app.services import BASE_PROMPT, RE_BASE_PROMPT
from app.schemas import Re_prompt
from typing import Annotated
from .auth import get_current_user
from app.models import  User_model, Project_model, Scene_model


router = APIRouter(prefix="/manim", tags=["Manim"])

@router.post("/generate/{prompt}")
async def generate(prompt: str, currentUser: Annotated[User_model, Depends(get_current_user)]) -> list:
    code = generate_code(f'{BASE_PROMPT}---This is user prompt:{prompt}---').text # get repsone in string from LLM
    generate_manim_file(settings.SCENES_PATH,code)
    edit_manim(settings.SCENES_PATH)

    scenes_list = parse_gemini_response(code) # parse the response
    
    a_scene_list= []
    # create scene instanse for each scene and store it in db
    for scene in scenes_list:
        a_scene = Scene_model(scene_name=scene.get("scene_name", None),
                              scene_code=scene.get("code", None),
                              video_path=Path(settings.VIDEO_PATH) / scene.get("scene_name", "scene") / "480p15" / f"{scene.get("scene_name", "scene")}.mp4",
                              scene_path=Path(settings.SCENES_FOLDER)/scene.get("scene_name", "scene"),
                              owner=currentUser)    
        await a_scene.create()
        a_scene_list.append(a_scene)
        print(f"Scene{a_scene.scene_name} added to db")

    project = Project_model(title="Project", 
                            description="Project Description", 
                            original_prompt=f'{BASE_PROMPT}---This is user prompt:{prompt}---',
                            scenes=a_scene_list,
                            scene_list=scenes_list,
                            project_path=Path(settings.MANIM_PATH),
                            owner=currentUser)
    await project.create()
    print(f"Project created")

    currentUser.projects.append(project)
    await currentUser.save()

    create_seperate_scenes(scenes_list)

    for scene in scenes_list:
        output = run_manim(settings.SCENES_FOLDER,scene_name=scene["scene_name"])
        print(f"Successfully runned scene: {scene["scene_name"]}")
        scene["ouptut"] = output
    return scenes_list

@router.get("/get_video/{project_name}/{scene_name}")
def get_video(scene_name, current_user: Annotated[User_model, Depends(get_current_user)]):
    video_path = Path(settings.VIDEO_PATH) / scene_name / "480p15" / f"{scene_name}.mp4"
    print(video_path)
    if video_path.exists():
        return FileResponse(media_type="video/mp4", path=video_path,filename=f'{scene_name}')
    return {"error": "video not found"}

@router.post("/re-prompt")
def re_prompt(body: Re_prompt):
    code = generate_code(RE_BASE_PROMPT.format(original_prompt=body.original_prompt,
                                               scene_name=body.scene_name,
                                               scene_code=body.code,
                                               scene_output=body.output,
                                               prompt=body.prompt)).text
    print(code)
    update_scene(body.scene_name,code)
    edit_scene(settings.MANIM_PATH/Path("scenes/"+body.scene_name+".py"))
    run_manim(settings.SCENES_FOLDER,scene_name=body.scene_name)
    return {"success":"scene updated"}