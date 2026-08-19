from pathlib import Path
import numpy as np


class EEGProcessor:
    """Traitement EEG avec calcul de fatigue"""

    def __init__(
        self,
        theta_min: float = 4.0,
        theta_max: float = 8.0,
        alpha_min: float = 8.0,
        alpha_max: float = 12.0,
        fatigue_ratio_min: float = 0.5,
        fatigue_ratio_max: float = 3.0,
    ):
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.fatigue_ratio_min = fatigue_ratio_min
        self.fatigue_ratio_max = fatigue_ratio_max

    def load_edf(self, psg_path: Path, picks: list[str] | None = None):
        """Charger fichier EDF avec MNE et retourner (sfreq, channels, data)"""
        import mne

        raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose=False)

        if picks is None:
            picks = ["Fpz-Cz", "Pz-Oz"]

        # Certains exports EDF préfixent les libellés (ex. "EEG Fpz-Cz" au lieu de
        # "Fpz-Cz") selon la version de MNE/l'origine du fichier -- on résout chaque
        # pick vers le vrai nom de canal par correspondance exacte puis par suffixe
        # avant de retomber sur les deux premiers canaux disponibles.
        resolved = []
        for pick in picks:
            if pick in raw.ch_names:
                resolved.append(pick)
                continue
            match = next((ch for ch in raw.ch_names if ch.lower().endswith(pick.lower())), None)
            if match:
                resolved.append(match)
        if not resolved:
            resolved = raw.ch_names[:2]

        raw = raw.copy().pick_channels(resolved)
        sfreq = float(raw.info["sfreq"])
        data = raw.get_data()  # (n_channels, n_samples)
        channels = list(raw.ch_names)
        return sfreq, channels, data

    def bandpower_fft(
        self,
        x: np.ndarray,
        sfreq: float,
        fmin: float,
        fmax: float,
    ) -> float:
        """
        Calcul puissance de bande via FFT.
        x: (n_samples,) ou compatible
        """
        x = np.asarray(x, dtype=np.float32)
        if x.size < 16:
            return 0.0

        # Detrend simple
        x = x - float(np.mean(x))

        n = x.size
        win = np.hanning(n).astype(np.float32)
        xw = x * win

        freqs = np.fft.rfftfreq(n, d=1.0 / sfreq)
        spec = np.abs(np.fft.rfft(xw)) ** 2

        band = (freqs >= fmin) & (freqs < fmax)
        if not np.any(band):
            return 0.0

        return float(np.mean(spec[band]))

    def compute_fatigue_score(self, window_2d: np.ndarray, sfreq: float) -> int:
        """
        Score fatigue 0-100 basé sur ratio theta/alpha.
        window_2d: (n_channels, n_samples)
        """
        if window_2d.size == 0:
            return 0

        # Moyenner les canaux
        x = np.mean(window_2d, axis=0)

        theta = self.bandpower_fft(x, sfreq, self.theta_min, self.theta_max)
        alpha = self.bandpower_fft(x, sfreq, self.alpha_min, self.alpha_max) + 1e-9

        ratio = theta / alpha

        # Mapper ratio vers 0-100
        norm = (ratio - self.fatigue_ratio_min) / (
            self.fatigue_ratio_max - self.fatigue_ratio_min
        )
        norm = max(0.0, min(1.0, norm))
        score = int(round(norm * 100))

        return score
