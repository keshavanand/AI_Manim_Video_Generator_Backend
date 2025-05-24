# Logic to save code, run manim, extract scenes
from pathlib import Path
import subprocess
from app.core import settings

def generate_manim_file(path: str, code:str):
    try:
        with open(path, "w") as file:
            file.write(code)
        print(f"\nFile '{path}' created successfully.\n")

    except Exception as e:
        print(f"\nAn error occurred while creating the file: {e}\n")

def run_manim(path:str):
    print("\n Running File\n")
    print("Current",path)
    try:
        cmd = f'python -m manim -ql {path} Demo'
        returned_value = subprocess.call(cmd,shell=True)
    except Exception as e:
        print(f"\nAn error occurred while executing manim the file: {e}\n")
    print('returned vale:', returned_value)


def edit_manim(path:str):
    with open(path,"r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines("scenes_list="+"\n")
        file.seek(12)
        file.writelines(lines[1:-1])

    print("\nFile Edited\n")

def create_seperate_scenes(scenes: list[dict]):
    for scene in scenes:
        generate_manim_file(settings.MANIM_PATH/Path(scene["scene_name"]+".py"), scene["code"])
        print(scene["scene_name"] + "Created")