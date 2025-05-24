# Environment/config loader
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os 

load_dotenv()

class Settings(BaseSettings):
    GEMINI_API: str = os.getenv("GEMINI_API","")
    MANIM_PATH: Path = r'C:\Users\arshd\OneDrive\Desktop\Web-App-Natural-Language-Manim-Video\manim-generator\manim'
    MANIM_MAIN_FILE_DIR: Path = r'C:/Users/arshd/OneDrive/Desktop/Web-App-Natural-Language-Manim-Video/manim-generator/manim/main.py'
    VIDEO_PATH: Path = r'C:\Users\arshd\OneDrive\Desktop\Web-App-Natural-Language-Manim-Video\manim-generator\fastapi-manim-ai-backend\media\videos\main\1080p60\Demo.mp4'
    SCENES_PATH: Path = r'C:\Users\arshd\OneDrive\Desktop\Web-App-Natural-Language-Manim-Video\manim-generator\fastapi-manim-ai-backend\app\services\scenes.py'
    
settings = Settings()

