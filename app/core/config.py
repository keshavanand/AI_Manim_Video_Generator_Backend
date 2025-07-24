# Environment/config loader
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os 

load_dotenv()

cwd = os.getcwd()
root = os.path.dirname(cwd)
class Settings_Deployment(BaseSettings):
    GEMINI_API: str = os.getenv("GEMINI_API","")
    MANIM_PATH: Path = fr'{cwd}/manim'
    MANIM_MAIN_FILE_DIR: Path = fr'{cwd}/manim/main.py'
    SCENES_PATH: Path = fr'{cwd}/manim/scenes.py'
    SCENES_FOLDER: Path = fr'{cwd}/manim/scenes'
    VIDEO_PATH: Path = fr'{cwd}/media/videos'

    MANIM_PROJECTS: Path = fr'{cwd}/Manim_Projects'


class Settings_Production(BaseSettings):
    GEMINI_API: str = os.getenv("GEMINI_API","")
    MANIM_PATH: Path = fr'{cwd}/manim'
    MANIM_MAIN_FILE_DIR: Path = fr'{cwd}/manim/main.py'
    SCENES_PATH: Path = fr'{cwd}/manim/scenes.py'
    SCENES_FOLDER: Path = fr'{cwd}/manim/scenes'
    VIDEO_PATH: Path = fr'{cwd}/media/videos'

    MANIM_PROJECTS: Path = fr'{cwd}/Manim_Projects'


settings = Settings_Deployment() if os.getenv("DEBUG") == "True" else Settings_Production()


