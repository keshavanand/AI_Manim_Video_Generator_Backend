 # FastAPI app entry point
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.db import lifespan

app = FastAPI(
    title="Manim Dashboard API",
    version="1.0.0",
    lifespan=lifespan
    )

app.include_router(api_router)