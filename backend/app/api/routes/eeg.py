import asyncio
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.api.routes.acquisition import active_sessions
from app.config import settings
from app.core.eeg_processor import EEGProcessor

router = APIRouter(prefix="/eeg", tags=["EEG"])

# Calibré pour EEG de sommeil (theta/alpha ratio 0.5–3.0)
processor_sleep = EEGProcessor(
    theta_min=settings.theta_min,
    theta_max=settings.theta_max,
    alpha_min=settings.alpha_min,
    alpha_max=settings.alpha_max,
    fatigue_ratio_min=settings.fatigue_ratio_min,
    fatigue_ratio_max=settings.fatigue_ratio_max,
)

# Calibré pour EEG éveillé / charge cognitive (ratio 0.3–1.5)
processor_eegmat = EEGProcessor(
    theta_min=settings.theta_min,
    theta_max=settings.theta_max,
    alpha_min=settings.alpha_min,
    alpha_max=settings.alpha_max,
    fatigue_ratio_min=0.3,
    fatigue_ratio_max=1.5,
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Canaux frontaux + pariétaux : frontal theta ↑ fatigue, pariétal alpha ↓ vigilance
EEGMAT_PICKS = ["EEG Fz", "EEG Pz", "EEG F3", "EEG F4", "EEG P3", "EEG P4"]
SLEEP_PICKS = ["Fpz-Cz", "Pz-Oz"]


def resolve_edf(dataset: str, subject: str, condition: str) -> tuple[Path, list[str]]:
    """Retourne (chemin_edf, channels_préférés) selon le dataset."""
    if dataset == "eegmat":
        cond_num = "1" if condition == "rest" else "2"
        path = DATA_DIR / "eegmat" / f"Subject{subject}_{cond_num}.edf"
        return path, EEGMAT_PICKS
    # default: sleep_edf
    return DATA_DIR / "sleep_edf" / "SC4001E0-PSG.edf", SLEEP_PICKS


@router.get("/datasets")
async def list_datasets():
    """Liste les fichiers EEGmat disponibles localement."""
    eegmat_dir = DATA_DIR / "eegmat"
    available = []
    if eegmat_dir.exists():
        for f in sorted(eegmat_dir.glob("Subject*_*.edf")):
            name = f.stem  # e.g. Subject00_1
            parts = name.split("_")
            if len(parts) == 2:
                subj = parts[0].replace("Subject", "")
                cond = "rest" if parts[1] == "1" else "task"
                available.append({
                    "subject": subj,
                    "condition": cond,
                    "label": f"Sujet {subj} — {'Repos' if cond == 'rest' else 'Tâche cognitive'}",
                    "filename": f.name,
                })
    return {"sleep_edf": True, "eegmat": available}


@router.websocket("/stream")
async def eeg_stream(
    ws: WebSocket,
    session_id: str = Query(None),
    dataset: str = Query("sleep"),
    subject: str = Query("00"),
    condition: str = Query("rest"),
):
    """WebSocket pour streaming EEG temps réel.

    Params:
      dataset   : "sleep" (défaut) | "eegmat"
      subject   : "00"–"02" pour eegmat
      condition : "rest" | "task" pour eegmat
    """
    await ws.accept()

    if not session_id or session_id not in active_sessions:
        await ws.send_json({"error": "Invalid or missing session_id"})
        await ws.close()
        return

    psg, picks = resolve_edf(dataset, subject, condition)

    if not psg.exists():
        await ws.send_json({"error": f"EDF file not found: {psg}"})
        await ws.close()
        return

    proc = processor_eegmat if dataset == "eegmat" else processor_sleep

    try:
        sfreq, channels, data = proc.load_edf(psg, picks=picks)
    except Exception as e:
        await ws.send_json({"error": f"Failed to load EDF: {type(e).__name__}: {e}"})
        await ws.close()
        return

    import numpy as np

    win_size = int(settings.fatigue_window_seconds * sfreq)
    n_ch = data.shape[0]
    buf = np.zeros((n_ch, win_size), dtype=np.float32)
    w_idx = 0
    filled = 0
    t0 = 0.0

    chunk_size = int(round(sfreq * settings.chunk_seconds))
    n_samples = data.shape[1]
    position = 0

    # Envoie le contexte du dataset au client
    context_label = (
        f"Sujet {subject} — {'Repos' if condition == 'rest' else 'Tâche cognitive'}"
        if dataset == "eegmat"
        else "Sleep-EDF (SC4001)"
    )

    try:
        while active_sessions.get(session_id, {}).get("status") == "running":
            if position >= n_samples:
                position = 0

            start = position
            end = min(start + chunk_size, n_samples)
            chunk = data[:, start:end].astype(np.float32)

            n_chunk = chunk.shape[1]
            if n_chunk == 0:
                await asyncio.sleep(0.01)
                continue

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

            if filled < win_size:
                window = buf[:, :filled]
            else:
                window = np.concatenate([buf[:, w_idx:], buf[:, :w_idx]], axis=1)

            score = proc.compute_fatigue_score(window, sfreq)

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
                "dataset": dataset,
                "dataset_label": context_label,
            }

            await ws.send_json(payload)

            active_sessions[session_id]["fatigue_score"] = score
            active_sessions[session_id]["quality"] = 85.0

            position = end
            t0 += (end - start) / sfreq

            await asyncio.sleep(settings.chunk_seconds)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"error": f"Stream error: {type(e).__name__}: {e}"})
        except Exception:
            pass
