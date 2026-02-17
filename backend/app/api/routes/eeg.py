import asyncio
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.core.eeg_processor import EEGProcessor

router = APIRouter(prefix="/eeg", tags=["EEG"])
processor = EEGProcessor(
    theta_min=settings.theta_min,
    theta_max=settings.theta_max,
    alpha_min=settings.alpha_min,
    alpha_max=settings.alpha_max,
    fatigue_ratio_min=settings.fatigue_ratio_min,
    fatigue_ratio_max=settings.fatigue_ratio_max,
)


@router.websocket("/stream")
async def eeg_stream(ws: WebSocket):
    """WebSocket pour streaming EEG temps réel"""
    await ws.accept()

    # Chemin au dataset EDF
    base = Path(__file__).resolve().parents[2]  # backend/app/
    psg = base / "data" / "sleep_edf" / "SC4001E0-PSG.edf"

    if not psg.exists():
        await ws.send_json({"error": f"EDF file not found: {psg}"})
        await ws.close()
        return

    try:
        sfreq, channels, data = processor.load_edf(psg)
    except Exception as e:
        await ws.send_json({
            "error": f"Failed to load EDF: {type(e).__name__}: {e}"
        })
        await ws.close()
        return

    # Ring buffer for fatigue window
    win_size = int(settings.fatigue_window_seconds * sfreq)
    n_ch = data.shape[0]
    import numpy as np
    buf = np.zeros((n_ch, win_size), dtype=np.float32)
    w_idx = 0
    filled = 0
    t0 = 0.0

    chunk_size = int(round(sfreq * settings.chunk_seconds))
    n_samples = data.shape[1]

    try:
        for start in range(0, n_samples, chunk_size):
            end = min(start + chunk_size, n_samples)
            chunk = data[:, start:end].astype(np.float32)

            n_chunk = chunk.shape[1]
            if n_chunk == 0:
                continue

            # Ajouter au ring buffer
            e = w_idx + n_chunk
            if e <= win_size:
                buf[:, w_idx:e] = chunk
            else:
                first = win_size - w_idx
                second = n_chunk - first
                buf[:, w_idx:win_size] = chunk[:, :first]
                buf[:, 0:second] = chunk[:, first:first + second]
            w_idx = (w_idx + n_chunk) % win_size
            filled = min(win_size, filled + n_chunk)

            # Reconstruire la fenêtre chronologique
            if filled < win_size:
                window = buf[:, :filled]
            else:
                window = np.concatenate([buf[:, w_idx:], buf[:, :w_idx]], axis=1)

            # Calculer score fatigue
            score = processor.compute_fatigue_score(window, sfreq)

            payload = {
                "t0": t0,
                "sfreq": sfreq,
                "channels": channels,
                "samples": chunk.tolist(),
                "fatigue": score,
                "quality": "Good",
                "alerts": [],
                "chunk_seconds": settings.chunk_seconds,
                "window_seconds": settings.fatigue_window_seconds,
            }

            await ws.send_json(payload)
            await asyncio.sleep(settings.chunk_seconds)

            t0 += (end - start) / sfreq

            if end >= n_samples:
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({
                "error": f"Stream error: {type(e).__name__}: {e}"
            })
        except Exception:
            pass
