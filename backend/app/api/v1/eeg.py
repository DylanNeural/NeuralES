from pathlib import Path
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.eeg_sleepedf import load_sleep_edf, iter_chunks, mock_fatigue

router = APIRouter(prefix="/eeg", tags=["EEG"])

@router.websocket("/stream")
async def eeg_stream(ws: WebSocket):
    await ws.accept()

    # Chemin dataset (adapter si tu bouges les fichiers)
    base = Path(__file__).resolve().parents[3]  # .../backend/app
    psg = base.parent / "data" / "sleep_edf" / "SC4001E0-PSG.edf"

    # Si tu gardes les EDF directement dans backend/ (comme sur ton screen) :
    # psg = base.parent / "SC4001E0-PSG.edf"

    sfreq, channels, data = load_sleep_edf(psg)

    try:
        for t0, samples in iter_chunks(data, sfreq, chunk_seconds=1.0):
            payload = {
                "t0": t0,
                "sfreq": sfreq,
                "channels": channels,
                "samples": samples,          # liste 2D
                "fatigue": mock_fatigue(samples),
                "quality": "Bonne",
                "alerts": [],
            }
            await ws.send_json(payload)
            await asyncio.sleep(1.0)  # simule temps réel
    except WebSocketDisconnect:
        return
