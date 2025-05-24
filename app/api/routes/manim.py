# Routes for LLM code input, editing, scene management
from fastapi import APIRouter
from app.services import generate_code
from app.core import settings
from app.services import generate_manim_file, edit_manim, run_manim, create_seperate_scenes,scenes_list
from fastapi.responses import FileResponse
BASE_PROMPT='''You are a Python expert who writes Manim scene code. Given a user description, generate valid Manim classes.

Your task is to divide the original animation into multiple separate Manim scenes, each representing one logical step or animation phase.This allows each scene to be rendered individually.

Important Instructions:
- Return the result as a JSON array of dictionaries.
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

@router.get("/generate/{prompt}")
def generate(prompt: str) -> str:
    code = generate_code(BASE_PROMPT+"---This is user prompt:{prompt}---").text
    generate_manim_file(settings.SCENES_PATH,code)
    edit_manim(settings.SCENES_PATH)
    create_seperate_scenes(scenes_list)
    #run_manim(settings.MANIM_MAIN_FILE_DIR)
    return code

@router.get("/get_video/")
def get_video():
    video_path = settings.VIDEO_PATH
    if video_path.exists():
        return FileResponse(media_type="video/mp4", path=video_path,filename="Demo.mp4")
    return {"error": "video not found"}