import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("command")

args = parser.parse_args()

if args.command == "run":
    os.system("uvicorn app.main:app --reload")
else:
    print("Unkown Command")