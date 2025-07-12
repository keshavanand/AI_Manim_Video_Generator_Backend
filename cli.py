import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("command")

args = parser.parse_args()

if args.command == "run":
    os.system("uvicorn app.main:app --reload")
if args.command == "celery":
    os.system("python -m celery -A app.core.celery_app.celery worker --loglevel=info --pool=solo")
if args.command == "flower":
    os.system("python -m celery -A app.core.celery_app.celery flower --port=5555 --pool=solo")
else:
    print("Unkown Command")