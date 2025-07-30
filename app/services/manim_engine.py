# old unused methods

# Logic to save code, run manim, extract scenes
from pathlib import Path
import subprocess
from app.core import settings
import os
from typing import List, Dict

def generate_manim_file(path: Path, code: str) -> None:
    """Write Manim code to a file."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(code)
    except Exception as e:
        # Use logging in production
        print(f"Error creating file {path}: {e}")

def run_manim(path: Path, scene_name: str) -> str:
    """Run Manim CLI for a given scene file and return output."""
    try:
        file_path = path / f"{scene_name}.py"
        cmd = f'python -m manim -ql "{file_path}" "{scene_name}"'
        return subprocess.check_output(cmd, text=True, shell=True)
    except Exception as e:
        print(f"Error running Manim for {scene_name}: {e}")
        return ""

def edit_manim(path: Path) -> None:
    """Edit main scenes file (custom logic)."""
    try:
        with open(path, "r+", encoding="utf-8") as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            file.write("scenes_list=\n")
            file.writelines(lines[1:-1])
    except Exception as e:
        print(f"Error editing file {path}: {e}")

def edit_scene(path: Path) -> None:
    """Edit a single scene file (custom logic)."""
    try:
        with open(path, "r+", encoding="utf-8") as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            file.writelines(lines[1:-1])
    except Exception as e:
        print(f"Error editing scene file {path}: {e}")

def create_seperate_scenes(scenes: List[Dict]) -> None:
    """Create separate files for each scene."""
    delete_all_files(settings.MANIM_PATH / "scenes")
    for scene in scenes:
        generate_manim_file(settings.MANIM_PATH / "scenes" / f"{scene['scene_name']}.py", scene["code"])

def create_single_scene(scene: Dict) -> None:
    """Create a single scene file."""
    generate_manim_file(settings.MANIM_PATH / "scenes" / f"{scene['scene_name']}.py", scene["code"])

def delete_all_files(path: Path) -> None:
    """Delete all files in a directory."""
    try:
        for file in os.listdir(path):
            os.remove(path / file)
    except Exception as e:
        print(f"Error deleting files in {path}: {e}")

def update_scene(scene_name: str, scene_code: str) -> None:
    """Update a scene file with new code."""
    generate_manim_file(settings.MANIM_PATH / "scenes" / f"{scene_name}.py", scene_code)