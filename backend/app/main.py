from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from pathlib import Path
import numpy as np

app = FastAPI(title="NeuralES API", version="0.1.0")

# Stream très fluide
CHUNK_SECONDS = 0.05          # 50 ms
FATIGUE_WINDOW_SECONDS = 10.0 # fenêtre glissante pour calcul


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


def load_sleep_edf(psg_path: Path, picks=None):
    import mne

    raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose=False)

    if picks is None:
        candidates = ["Fpz-Cz", "Pz-Oz"]
        picks = [ch for ch in candidates if ch in raw.ch_names]
        if not picks:
            picks = raw.ch_names[:2]

    raw = raw.copy().pick_channels(picks)
    sfreq = float(raw.info["sfreq"])
    data = raw.get_data()  # (n_channels, n_samples)
    channels = raw.ch_names
    return sfreq, channels, data


def bandpower_fft(x: np.ndarray, sfreq: float, fmin: float, fmax: float) -> float:
    """
    Puissance de bande via FFT (rapide, stable).
    x: (n_samples,) float
    """
    x = np.asarray(x, dtype=np.float32)
    if x.size < 16:
        return 0.0

    # detrend simple
    x = x - float(np.mean(x))

    n = x.size
    win = np.hanning(n).astype(np.float32)
    xw = x * win

    freqs = np.fft.rfftfreq(n, d=1.0 / sfreq)
    spec = np.abs(np.fft.rfft(xw)) ** 2  # power spectrum (non normalisé)

    band = (freqs >= fmin) & (freqs < fmax)
    if not np.any(band):
        return 0.0

    return float(np.mean(spec[band]))


def fatigue_score_from_window(window_2d: np.ndarray, sfreq: float) -> int:
    """
    Score fatigue 0-100 basé sur ratio theta/alpha sur la fenêtre.
    window_2d: shape (n_channels, n_samples_window)
    """
    if window_2d.size == 0:
        return 0

    # On moyenne les canaux (simple + robuste)
    x = np.mean(window_2d, axis=0)

    theta = bandpower_fft(x, sfreq, 4.0, 8.0)
    alpha = bandpower_fft(x, sfreq, 8.0, 12.0) + 1e-9

    ratio = theta / alpha  # fatigue ↑ quand ratio ↑ (heuristique)

    # Mapping ratio -> score (borné et lissé)
    # Ajuste ces bornes si besoin
    r_min, r_max = 0.5, 3.0
    norm = (ratio - r_min) / (r_max - r_min)
    norm = max(0.0, min(1.0, norm))
    score = int(round(norm * 100))

    return score


@app.websocket("/eeg/stream")
async def eeg_stream(ws: WebSocket):
    await ws.accept()

    psg = Path(__file__).resolve().parent / "data" / "sleep_edf" / "SC4001E0-PSG.edf"
    if not psg.exists():
        await ws.send_json({"error": f"EDF introuvable: {psg}"})
        await ws.close()
        return

    try:
        sfreq, channels, data = load_sleep_edf(psg)
    except Exception as e:
        await ws.send_json({"error": f"Erreur chargement EDF: {type(e).__name__}: {e}"})
        await ws.close()
        return

    # Ring buffer pour fenêtre fatigue
    win_size = int(FATIGUE_WINDOW_SECONDS * sfreq)
    n_ch = data.shape[0]
    buf = np.zeros((n_ch, win_size), dtype=np.float32)
    w_idx = 0
    filled = 0
    t0 = 0.0

    # chunk size
    chunk_size = int(round(sfreq * CHUNK_SECONDS))
    n_samples = data.shape[1]

    try:
        for start in range(0, n_samples, chunk_size):
            end = min(start + chunk_size, n_samples)
            chunk = data[:, start:end].astype(np.float32)  # (n_ch, n_chunk)

            # push chunk into fatigue window buffer (ring)
            n_chunk = chunk.shape[1]
            if n_chunk == 0:
                continue

            # write with wrap
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

            # get window in chronological order for FFT
            if filled < win_size:
                window = buf[:, :filled]
            else:
                # reconstruct [w_idx .. end] + [0 .. w_idx)
                window = np.concatenate([buf[:, w_idx:], buf[:, :w_idx]], axis=1)

            score = fatigue_score_from_window(window, sfreq)

            payload = {
                "t0": t0,
                "sfreq": sfreq,
                "channels": channels,
                "samples": chunk.tolist(),       # chunk courant (petit)
                "fatigue": score,                # ✅ score temps réel
                "quality": "Bonne",
                "alerts": [],
                "chunk_seconds": CHUNK_SECONDS,
                "window_seconds": FATIGUE_WINDOW_SECONDS,
            }

            await ws.send_json(payload)
            await asyncio.sleep(CHUNK_SECONDS)

            t0 += (end - start) / sfreq

            if end >= n_samples:
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"error": f"Erreur stream: {type(e).__name__}: {e}"})
        except Exception:
            pass
