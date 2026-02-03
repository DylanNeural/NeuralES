# desktop/app/pages/acquisition.py

import json
import numpy as np

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy
)

import pyqtgraph as pg

WS_URL = "ws://127.0.0.1:8000/eeg/stream"

# Perf global
pg.setConfigOptions(useOpenGL=True, antialias=False)


class AcquisitionPage(QWidget):
    def __init__(self, on_stop=None):
        super().__init__()
        self.on_stop = on_stop

        # --- état ---
        self.paused = False

        # --- ring buffer ---
        self.sfreq = None
        self.channels = []
        self.window_seconds = 10.0

        self.max_samples = 0
        self.x = None              # (max_samples,)
        self.y = None              # (n_channels, max_samples)
        self.write_idx = 0
        self.count = 0
        self.t = 0.0

        # --- UI ---
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        title = QLabel("Acquisition en temps réel")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        root.addWidget(title)

        self.lbl_info = QLabel("Connexion EEG : en attente…")
        self.lbl_info.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 8px;")
        root.addWidget(self.lbl_info)

        row = QHBoxLayout()
        row.setSpacing(12)
        root.addLayout(row, 1)

        # --- Plot ---
        left = QVBoxLayout()
        row.addLayout(left, 2)

        plot_title = QLabel("Signaux EEG")
        plot_title.setStyleSheet("font-weight: 600;")
        left.addWidget(plot_title)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(None)
        self.plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot.setMinimumHeight(360)
        left.addWidget(self.plot)

        self.plot.addLegend(offset=(10, 10))

        # PlotItem (les options perf sont ici)
        self.pitem = self.plot.getPlotItem()
        self.pitem.setClipToView(True)
        self.pitem.setDownsampling(mode="peak")  # ok sur la plupart des versions
        self.pitem.setLabel("bottom", "Temps (s)")
        self.pitem.setLabel("left", "Amplitude (brut)")
        self.pitem.showGrid(x=True, y=True, alpha=0.2)

        # Certaines versions ont autoDownsample comme option interne :
        # pas indispensable, on ne dépend pas dessus.

        self.curves = []

        # --- Panel droite ---
        right = QVBoxLayout()
        row.addLayout(right, 1)

        fatigue_title = QLabel("Niveau de fatigue")
        fatigue_title.setStyleSheet("font-weight: 600;")
        right.addWidget(fatigue_title)

        self.lbl_fatigue = QLabel("Score actuel : — / 100")
        right.addWidget(self.lbl_fatigue)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(14)
        self.bar.setTextVisible(False)
        right.addWidget(self.bar)

        self.lbl_chunk = QLabel("Chunk : —")
        self.lbl_chunk.setStyleSheet("color: #555;")
        right.addWidget(self.lbl_chunk)

        self.lbl_alerts_title = QLabel("Alertes")
        self.lbl_alerts_title.setStyleSheet("margin-top: 12px; font-weight: 600;")
        right.addWidget(self.lbl_alerts_title)

        self.lbl_alerts = QLabel("Aucune alerte pour le moment")
        self.lbl_alerts.setStyleSheet("color: #777;")
        right.addWidget(self.lbl_alerts)

        right.addStretch(1)

        # --- Buttons ---
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self._toggle_pause)
        actions.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("Arrêter & enregistrer")
        self.btn_stop.setStyleSheet("background:#d9534f; color:white; padding:6px 10px; border-radius:8px;")
        self.btn_stop.clicked.connect(self._stop)
        actions.addWidget(self.btn_stop)

        actions.addStretch(1)
        root.addLayout(actions)

        # --- WebSocket ---
        self.ws = QWebSocket()
        self.ws.connected.connect(self._on_ws_connected)
        self.ws.disconnected.connect(self._on_ws_disconnected)
        self.ws.textMessageReceived.connect(self._on_ws_msg)
        self.ws.errorOccurred.connect(self._on_ws_error)
        self.ws.open(QUrl(WS_URL))

        # --- Timer rendu (60 FPS) ---
        self.render_timer = QTimer(self)
        self.render_timer.setInterval(16)
        self.render_timer.timeout.connect(self._render)
        self.render_timer.start()

    # ---------------- WS ----------------

    def _on_ws_connected(self):
        self.lbl_info.setText(f"Connexion EEG : OK ({WS_URL})")

    def _on_ws_disconnected(self):
        self.lbl_info.setText("Connexion EEG : fermée")

    def _on_ws_error(self, err):
        self.lbl_info.setText(f"Connexion EEG : ERREUR ({err})")

    def _on_ws_msg(self, msg: str):
        if self.paused:
            return

        data = json.loads(msg)

        if "error" in data:
            self.lbl_info.setText(f"Connexion EEG : ERREUR ({data['error']})")
            return

        fatigue = int(data.get("fatigue", 0))
        self.lbl_fatigue.setText(f"Score actuel : {fatigue} / 100")
        self.bar.setValue(fatigue)

        sfreq = float(data.get("sfreq", 0.0))
        channels = data.get("channels", [])
        samples = data.get("samples", [])
        t0 = float(data.get("t0", 0.0))
        alerts = data.get("alerts", [])

        n_ch = len(samples)
        n_samp = len(samples[0]) if n_ch else 0
        self.lbl_chunk.setText(f"t0={t0:.2f}s | {n_ch} canaux x {n_samp} samples")
        self.lbl_alerts.setText("\n".join(map(str, alerts)) if alerts else "Aucune alerte pour le moment")

        if self.sfreq != sfreq or self.channels != channels or self.x is None:
            self._init_buffers(sfreq, channels)

        self._push_chunk(samples)

    # ------------- Ring buffer -------------

    def _init_buffers(self, sfreq: float, channels: list):
        self.sfreq = sfreq
        self.channels = list(channels)

        self.max_samples = int(self.window_seconds * self.sfreq)
        if self.max_samples < 200:
            self.max_samples = 200

        self.x = np.zeros((self.max_samples,), dtype=np.float32)
        self.y = np.zeros((len(self.channels), self.max_samples), dtype=np.float32)
        self.write_idx = 0
        self.count = 0
        self.t = 0.0

        self.plot.clear()
        self.plot.addLegend(offset=(10, 10))
        self.curves = []
        for ch in self.channels:
            self.curves.append(self.plot.plot([], [], name=ch))

    def _push_chunk(self, samples_2d):
        if not samples_2d or self.y is None:
            return

        n_ch = min(len(samples_2d), self.y.shape[0])
        n_samp = len(samples_2d[0]) if n_ch else 0
        if n_samp == 0:
            return

        dt = 1.0 / float(self.sfreq)

        t_chunk = self.t + dt * (np.arange(n_samp, dtype=np.float32) + 1.0)
        self.t = float(t_chunk[-1])

        w = self.write_idx
        end = w + n_samp

        if end <= self.max_samples:
            self.x[w:end] = t_chunk
            for c in range(n_ch):
                self.y[c, w:end] = np.asarray(samples_2d[c], dtype=np.float32)
        else:
            first = self.max_samples - w
            second = n_samp - first

            self.x[w:self.max_samples] = t_chunk[:first]
            self.x[0:second] = t_chunk[first:]

            for c in range(n_ch):
                arr = np.asarray(samples_2d[c], dtype=np.float32)
                self.y[c, w:self.max_samples] = arr[:first]
                self.y[c, 0:second] = arr[first:]

        self.write_idx = (w + n_samp) % self.max_samples
        self.count = min(self.max_samples, self.count + n_samp)

    def _get_view(self):
        if self.count == 0 or self.x is None:
            return None, None

        n = self.count
        w = self.write_idx
        start = (w - n) % self.max_samples

        if start < w:
            x_view = self.x[start:w]
            y_view = self.y[:, start:w]
        else:
            x_view = np.concatenate([self.x[start:], self.x[:w]])
            y_view = np.concatenate([self.y[:, start:], self.y[:, :w]], axis=1)

        return x_view, y_view

    # ------------- Render loop -------------

    def _render(self):
        if self.paused or self.x is None or not self.curves:
            return

        x_view, y_view = self._get_view()
        if x_view is None:
            return

        max_points = 2000
        m = x_view.shape[0]
        if m > max_points:
            step = max(1, m // max_points)
            x_plot = x_view[::step]
            y_plot = y_view[:, ::step]
        else:
            x_plot = x_view
            y_plot = y_view

        for i, curve in enumerate(self.curves):
            curve.setData(x_plot, y_plot[i])

        if x_plot.size > 2:
            self.plot.setXRange(float(x_plot[-1] - self.window_seconds), float(x_plot[-1]), padding=0)

    # ------------- Buttons -------------

    def _toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.setText("Reprendre" if self.paused else "Pause")

    def _stop(self):
        try:
            self.ws.close()
        except Exception:
            pass
        if self.on_stop:
            self.on_stop()
