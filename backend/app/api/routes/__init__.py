from .organisations import router as organisations_router
from .eeg import router as eeg_router
from .health import router as health_router

__all__ = [
    "organisations_router",
    "eeg_router",
    "health_router",
]
