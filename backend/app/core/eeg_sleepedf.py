from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class EEGChunk:
    t0: float
    sfreq: float
    channels: list[str]
    samples: list[list[float]]  # shape: (n_channels, n_samples)

def load_sleep_edf(psg_path: Path, picks: list[str] | None = None):
    """
    Retourne (raw, sfreq, channels, data ndarray [n_channels, n_samples])
    """
    import mne

    raw = mne.io.read_raw_edf(psg_path, preload=True, verbose=False)

    if picks is None:
        # Sleep-EDF typique : 2 EEG
        candidates = ["Fpz-Cz", "Pz-Oz"]
        picks = [ch for ch in candidates if ch in raw.ch_names]
        if not picks:
            # fallback: prendre les 2 premiers canaux
            picks = raw.ch_names[:2]

    raw = raw.copy().pick_channels(picks)
    sfreq = float(raw.info["sfreq"])
    data = raw.get_data()  # numpy array (n_channels, n_samples)
    channels = raw.ch_names
    return sfreq, channels, data

def iter_chunks(data: np.ndarray, sfreq: float, chunk_seconds: float = 1.0):
    """
    Générateur : yield EEGChunk toutes les chunk_seconds.
    data shape: (n_channels, n_samples)
    """
    n_channels, n_samples = data.shape
    chunk_size = int(round(sfreq * chunk_seconds))
    t0 = 0.0

    for start in range(0, n_samples, chunk_size):
        end = min(start + chunk_size, n_samples)
        samples = data[:, start:end].tolist()
        yield t0, samples
        t0 += (end - start) / sfreq
        if end >= n_samples:
            break

def mock_fatigue(samples: list[list[float]]) -> int:
    """
    Score fatigue fake mais stable : basé sur énergie RMS + lissage léger.
    """
    arr = np.array(samples, dtype=float)
    rms = float(np.sqrt(np.mean(arr * arr)))
    # map grossier vers 0..100
    score = int(max(0, min(100, (rms / (rms + 50.0)) * 100.0)))
    return score
