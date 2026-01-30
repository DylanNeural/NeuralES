from fastapi import APIRouter
from app.api.v1.eeg import router as eeg_router

api_router = APIRouter()
api_router.include_router(eeg_router)
