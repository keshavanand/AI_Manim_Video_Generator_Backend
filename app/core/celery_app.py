from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

broker_url ="redis://localhost:6379/0" if os.getenv("DEBUG") == "True" else "redis://redis:6379/0"
if os.getenv("REDIS_URL"):
    broker_url = os.getenv("REDIS_URL")
celery = Celery("manim_backend", broker=broker_url)

# Import tasks so Celery can register them
import app.core.tasks