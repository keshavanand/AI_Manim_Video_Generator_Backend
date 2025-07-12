from celery import Celery

celery = Celery("manim_backend", broker="redis://localhost:6379/0")

# Import tasks so Celery can register them
import app.core.tasks