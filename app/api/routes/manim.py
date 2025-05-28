# Routes for LLM code input, editing, scene management
from pathlib import Path
from fastapi import APIRouter
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes, parse_gemini_response, update_scene, edit_scene
from fastapi.responses import FileResponse
from app.services import BASE_PROMPT, RE_BASE_PROMPT
from app.schemas import Re_prompt

router = APIRouter(prefix="/manim", tags=["Manim"])

@router.post("/generate/{prompt}")
def generate(prompt: str) -> list:
    code = generate_code(f'{BASE_PROMPT}---This is user prompt:{prompt}---').text
    generate_manim_file(settings.SCENES_PATH,code)
    edit_manim(settings.SCENES_PATH)

    scenes_list = parse_gemini_response(code)
    
    create_seperate_scenes(scenes_list)

    for scene in scenes_list:
        output = run_manim(settings.SCENES_FOLDER,scene_name=scene["scene_name"])
        print(f"Successfully runned scene: {scene["scene_name"]}")
        scene["ouptut"] = output
    return scenes_list

@router.get("/get_video/{scene_name}")
def get_video(scene_name):
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