from fastapi import APIRouter
from .project import router as project_router
from .scene import router as scene_router
from .media import router as media_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(project_router)
router.include_router(scene_router)
router.include_router(media_router)
