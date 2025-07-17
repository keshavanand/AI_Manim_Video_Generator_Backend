import argparse
import os
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("command")

args = parser.parse_args()

if args.command == "run":
    os.system("uvicorn app.main:app --reload")
if args.command == "celery":
    worker_id = uuid.uuid4().hex[:8]
    hostname = f"worker_{worker_id}@%h"

    os.system(f"python -m celery -A app.core.celery_app.celery worker --loglevel=info --pool=solo --hostname={hostname}")
if args.command == "flower":
    os.system("python -m celery -A app.core.celery_app.celery flower --port=5555 --pool=solo")
else:
    print("Unkown Command")