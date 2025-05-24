from fastapi import APIRouter
from .manim import router as manim_router

router = APIRouter()
router.include_router(manim_router)