from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from app.models import User as User_model, Project as Project_model, Scene as Scene_model, ChatMessage, Media
from dotenv import load_dotenv
import os
from app.core.logging_config import logger
load_dotenv()

db_url = "mongodb://localhost:27017" if os.getenv("DEBUG") == "True" else "mongodb://db:27017"
if os.getenv("DB_URL"):
    db_url= os.getenv("DB_URL")
async def init_beanie_db():
    """
    Initialize Beanie ODM for MongoDB. Can be used in FastAPI or Celery worker.
    """
    client = AsyncIOMotorClient(db_url)
    db = client["manim"]
    await init_beanie(
        database=db,
        document_models=[User_model, Project_model, Scene_model, ChatMessage, Media]
    )
    # Do not close client here; let the process manage it

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie_db()
    logger.info("Connected to database successfuly")
    yield  # Serve application
