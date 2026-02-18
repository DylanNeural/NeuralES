from .organisations import router as organisations_router
from .eeg import router as eeg_router
from .health import router as health_router
from .auth import router as auth_router
from .acquisition import router as acquisition_router
from .patients import router as patients_router
from .results import router as results_router
from .devices import router as devices_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "organisations_router",
    "eeg_router",
    "health_router",
    "acquisition_router",
    "patients_router",
    "results_router",
    "devices_router",
    "analytics_router",
]
