# Routes for LLM code input, editing, scene management
from pathlib import Path
from fastapi import APIRouter
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes, parse_gemini_response
from fastapi.responses import FileResponse
import os
BASE_PROMPT='''You are a Python expert who writes Manim scene code. Given a user description, generate valid Manim classes.

Your task is to divide the original animation into multiple separate Manim scenes, each representing one logical step or animation phase.This allows each scene to be rendered individually.

Important Instructions:
- Return the result as a json list of dictionaries.
- Each dictionary must have:
  - "scene_name": A unique name like Intro, Showing Dots etc.. based on the user request
  - "code": A string containing the full raw Python code for that specific scene.
- Only return the JSON array. Do not add any explanations or extra text.

Example output format:
[
  {
    "scene_name": "Intro",
    "code": "from manim import *\\n\\nclass Intro(Scene):\\n    def construct(self):\\n        Code for intro scene"
  },
  {
    "scene_name": "Showing_Dots",
    "code": "from manim import *\\n\\nclass Showing_Dots(Scene):\\n    def construct(self):\\n        Code for showing dots"
  }
]
'''

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

@router.post("/re-prompt/{prompt}")
def re_prompt(prompt):
    pass