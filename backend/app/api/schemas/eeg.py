from pydantic import BaseModel, Field


class EEGStreamPayload(BaseModel):
    """Payload EEG émis via WebSocket"""
    t0: float = Field(description="Timestamp de départ du chunk (secondes)")
    sfreq: float = Field(description="Fréquence d'échantillonnage (Hz)")
    channels: list[str] = Field(description="Noms des canaux EEG")
    samples: list[list[float]] = Field(description="Samples (n_channels x n_samples)")
    fatigue: int = Field(ge=0, le=100, description="Score fatigue 0-100")
    quality: str = Field(description="Qualité du signal")
    alerts: list[str] = Field(default_factory=list, description="Alertes détectées")
    chunk_seconds: float = Field(description="Durée du chunk")
    window_seconds: float = Field(description="Fenêtre glissante pour calcul")
