from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager

from app.models import User, Project, Scene

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB client
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["manim"]

    # Initialize Beanie with document models
    await init_beanie(
        database=db,
        document_models=[User, Project, Scene]
    )

    yield  # Serve application

    # Cleanup
    client.close()
