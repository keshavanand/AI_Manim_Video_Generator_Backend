from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from app.models import User as User_model, Project as Project_model, Scene as Scene_model, ChatMessage, Media

async def init_beanie_db():
    """
    Initialize Beanie ODM for MongoDB. Can be used in FastAPI or Celery worker.
    """
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["manim"]
    await init_beanie(
        database=db,
        document_models=[User_model, Project_model, Scene_model, ChatMessage, Media]
    )
    # Do not close client here; let the process manage it

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie_db()
    yield  # Serve application
