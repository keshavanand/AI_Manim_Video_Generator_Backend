# Logic to save code, run manim, extract scenes
from pathlib import Path
import subprocess
from app.core import settings
import os

def generate_manim_file(path: str, code:str):
    try:
        with open(path, "w") as file:
            file.write(code)
        print(f"\nFile '{path}' created successfully.\n")

    except Exception as e:
        print(f"\nAn error occurred while creating the file: {e}\n")

def run_manim(path:str, scene_name:str):
    print(f"\n Running File {scene_name}")
    returned_value = ""
    try:
        file_path = os.path.join(path, f"{scene_name}.py")
        cmd = f'python -m manim -ql "{file_path}" "{scene_name}"'
        returned_value = subprocess.check_output(cmd,text=True, shell=True)
    except Exception as e:
        print(f"\nAn error occurred while executing manim the file: {e}\n")
    return returned_value


def edit_manim(path:str):
    with open(path,"r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines("scenes_list="+"\n")
        file.seek(12)
        file.writelines(lines[1:-1])

    print("\nFile Edited\n")

def edit_scene(path:str):
    with open(path,"r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(lines[1:-1])

    print("\nFile Edited\n")

def create_seperate_scenes(scenes: list[dict]):
    delete_all_files(settings.MANIM_PATH/Path("scenes/"))
    for scene in scenes:
        generate_manim_file(settings.MANIM_PATH/Path("scenes/"+scene["scene_name"]+".py"), scene["code"])
        print(scene["scene_name"] + "Created")

def delete_all_files(path: Path):
    try:
        for file in os.listdir(path):
            os.remove(path/Path(file))
            print(f"Deleted {file}")
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")

def update_scene(scene_name: str,scene_code:str):
    generate_manim_file(settings.MANIM_PATH/Path("scenes/"+scene_name+".py"), scene_code)