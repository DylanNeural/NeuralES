import json
import numpy as np

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QFrame
)

import pyqtgraph as pg

from app.ui.brain_view import BrainView
from app.ui.chart3d_view import Chart3DView

API_BASE = "http://127.0.0.1:8000"
WS_BASE  = "ws://127.0.0.1:8000"
pg.setConfigOptions(useOpenGL=False, antialias=False)


class AcquisitionPage(QWidget):
    def __init__(self, on_stop=None):
        super().__init__()
        self.on_stop = on_stop
        self.paused  = False

        # EEG state
        self.sfreq    = None
        self.channels = []
        self.window_seconds = 10.0
        self.max_samples = 0
        self.x = self.y = None
        self.write_idx = self.count = 0
        self.t = 0.0
        self.session_id = None

        # Electrodes sélectionnées (depuis Three.js)
        self.active_electrodes: list[str] = []

        # HTTP client pour créer/stopper la session
        self._nam = QNetworkAccessManager(self)

        # ── Layout principal ──
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._topo_mode = False

        # ── Barre de titre ──
        title_bar = QFrame()
        title_bar.setStyleSheet("background: white; border-bottom: 1px solid #E5E7EB;")
        title_bar.setFixedHeight(52)
        tbl = QHBoxLayout(title_bar)
        tbl.setContentsMargins(18, 0, 18, 0)

        title = QLabel("Acquisition en temps réel")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")

        # Toggle Signaux / Topographie
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet(
            "background: #F3F4F6; border-radius: 8px; border: 1px solid #E5E7EB;"
        )
        toggle_frame.setFixedHeight(34)
        tfl = QHBoxLayout(toggle_frame)
        tfl.setContentsMargins(3, 3, 3, 3)
        tfl.setSpacing(2)

        self.btn_signals = QPushButton("Signaux EEG")
        self.btn_topo    = QPushButton("Vue 3D")
        for btn in (self.btn_signals, self.btn_topo):
            btn.setFixedHeight(26)
            btn.setStyleSheet("""
                QPushButton {
                    border: none; border-radius: 6px;
                    font-size: 12px; font-weight: 600;
                    padding: 0 12px;
                    background: transparent; color: #6B7280;
                }
            """)
        self.btn_signals.clicked.connect(lambda: self._set_mode(False))
        self.btn_topo.clicked.connect(lambda: self._set_mode(True))
        tfl.addWidget(self.btn_signals)
        tfl.addWidget(self.btn_topo)
        self._set_mode(False, init=True)  # active Signaux par défaut

        self.lbl_info = QLabel("EEG : en attente…")
        self.lbl_info.setStyleSheet("color: #6B7280; font-size: 12px;")

        tbl.addWidget(title)
        tbl.addStretch(1)
        tbl.addWidget(toggle_frame)
        tbl.addSpacing(16)
        tbl.addWidget(self.lbl_info)
        root.addWidget(title_bar)

        # ── Zone centrale ──
        center = QHBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(0)
        root.addLayout(center, 1)

        # ── Colonne principale (chart + brain) ──
        main_col = QVBoxLayout()
        main_col.setContentsMargins(0, 0, 0, 0)
        main_col.setSpacing(0)
        center.addLayout(main_col, 1)

        # ── Haut : graphe EEG ──
        chart_panel = QFrame()
        chart_panel.setStyleSheet("background: #F8FAFC; border-bottom: 1px solid #E5E7EB;")
        cpl = QVBoxLayout(chart_panel)
        cpl.setContentsMargins(12, 12, 12, 12)
        cpl.setSpacing(8)

        chart_header = QLabel("Signaux EEG")
        chart_header.setStyleSheet("font-weight: 600; color: #374151;")
        cpl.addWidget(chart_header)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(None)
        self.plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot.addLegend(offset=(10, 10))
        pi = self.plot.getPlotItem()
        pi.setClipToView(True)
        pi.setDownsampling(mode="peak")
        pi.setLabel("bottom", "Temps (s)")
        pi.setLabel("left",   "Amplitude (µV)")
        pi.showGrid(x=True, y=True, alpha=0.15)
        self.curves = []
        cpl.addWidget(self.plot, 1)

        self.lbl_chunk = QLabel("—")
        self.lbl_chunk.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        cpl.addWidget(self.lbl_chunk)

        chart_panel.setMinimumHeight(220)
        self.chart_panel = chart_panel
        main_col.addWidget(chart_panel, 2)

        # ── Vue 3D (cachée par défaut) ──
        self.chart3d = Chart3DView()
        self.chart3d.setVisible(False)
        self.chart3d.setMinimumHeight(220)
        main_col.addWidget(self.chart3d, 2)

        # ── Bas : cerveau 3D ──
        brain_panel = QFrame()
        brain_panel.setStyleSheet("background: #0F172A;")
        bpl = QVBoxLayout(brain_panel)
        bpl.setContentsMargins(0, 0, 0, 0)
        bpl.setSpacing(0)

        self.brain = BrainView()
        self.brain.electrodes_changed.connect(self._on_electrodes_changed)
        bpl.addWidget(self.brain, 1)

        self.lbl_electrodes = QLabel("Aucune électrode sélectionnée")
        self.lbl_electrodes.setStyleSheet(
            "color: #94A3B8; font-size: 11px; padding: 6px 10px;"
            "background: #0F172A; border-top: 1px solid #1E293B;"
        )
        self.lbl_electrodes.setWordWrap(True)
        bpl.addWidget(self.lbl_electrodes)

        main_col.addWidget(brain_panel, 1)

        # ── Droite : fatigue ──
        right_panel = QFrame()
        right_panel.setFixedWidth(220)
        right_panel.setStyleSheet(
            "background: white; border-left: 1px solid #E5E7EB;"
        )
        rpl = QVBoxLayout(right_panel)
        rpl.setContentsMargins(16, 16, 16, 16)
        rpl.setSpacing(12)

        fat_title = QLabel("Niveau de fatigue")
        fat_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        rpl.addWidget(fat_title)

        self.lbl_fatigue = QLabel("— / 100")
        self.lbl_fatigue.setStyleSheet("font-size: 28px; font-weight: 700; color: #2563EB;")
        rpl.addWidget(self.lbl_fatigue)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(10)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet("""
            QProgressBar { background: #E5E7EB; border-radius: 5px; border: none; }
            QProgressBar::chunk { background: #2563EB; border-radius: 5px; }
        """)
        rpl.addWidget(self.bar)

        self.lbl_status = QLabel("En attente")
        self.lbl_status.setStyleSheet(
            "color: #6B7280; font-size: 12px; padding: 6px 10px;"
            "background: #F3F4F6; border-radius: 8px;"
        )
        rpl.addWidget(self.lbl_status)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E5E7EB; margin-top: 4px;")
        rpl.addWidget(sep)

        alerts_title = QLabel("Alertes")
        alerts_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        rpl.addWidget(alerts_title)

        self.lbl_alerts = QLabel("Aucune alerte")
        self.lbl_alerts.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        self.lbl_alerts.setWordWrap(True)
        rpl.addWidget(self.lbl_alerts)

        rpl.addStretch(1)

        # Boutons
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setFixedHeight(36)
        self.btn_pause.setStyleSheet("""
            QPushButton { background:#F3F4F6; color:#374151; border:1px solid #D1D5DB;
                          border-radius:8px; font-weight:600; }
            QPushButton:hover { background:#E5E7EB; }
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)
        rpl.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("Arrêter & enregistrer")
        self.btn_stop.setFixedHeight(36)
        self.btn_stop.setStyleSheet("""
            QPushButton { background:#EF4444; color:white; border:none;
                          border-radius:8px; font-weight:600; }
            QPushButton:hover { background:#DC2626; }
        """)
        self.btn_stop.clicked.connect(self._stop)
        rpl.addWidget(self.btn_stop)

        center.addWidget(right_panel)

        # ── WebSocket (ouvert après création de session) ──
        self.ws = QWebSocket()
        self.ws.connected.connect(self._on_ws_connected)
        self.ws.disconnected.connect(self._on_ws_disconnected)
        self.ws.textMessageReceived.connect(self._on_ws_msg)
        self.ws.errorOccurred.connect(self._on_ws_error)

        # Créer la session via l'API REST
        self._start_session()

        # ── Timer rendu 60 FPS ──
        self.render_timer = QTimer(self)
        self.render_timer.setInterval(16)
        self.render_timer.timeout.connect(self._render)
        self.render_timer.start()

    # ── Scores par électrode depuis les amplitudes brutes ──

    def _compute_electrode_scores(self, channels: list, samples: list) -> dict:
        """Calcule un score 0-100 par électrode depuis l'amplitude RMS de chaque canal.
        Ex: canal 'Fpz-Cz' → électrodes Fpz et Cz reçoivent le même score."""
        result = {}
        for ch_name, ch_samples in zip(channels, samples):
            if not ch_samples:
                continue
            arr = np.asarray(ch_samples, dtype=np.float32)
            rms = float(np.sqrt(np.mean(arr ** 2)))
            # Normalisation : 0 µV → 0, 80 µV → 100 (typique EEG sommeil)
            score = int(min(100, max(0, rms / 80.0 * 100)))
            # Mapper chaque électrode du canal (ex: "Fpz-Cz" → Fpz et Cz)
            for elec in ch_name.replace('-', ' ').split():
                result[elec] = score
        return result

    # ── Toggle mode ──

    def _set_mode(self, topo: bool, init: bool = False):
        self._topo_mode = topo

        active_style = (
            "QPushButton { border: none; border-radius: 6px; font-size: 12px;"
            " font-weight: 600; padding: 0 12px; background: white; color: #111827; }"
        )
        inactive_style = (
            "QPushButton { border: none; border-radius: 6px; font-size: 12px;"
            " font-weight: 600; padding: 0 12px; background: transparent; color: #6B7280; }"
        )
        self.btn_topo.setStyleSheet(active_style if topo else inactive_style)
        self.btn_signals.setStyleSheet(inactive_style if topo else active_style)

        if init:
            return

        if hasattr(self, 'chart_panel'):
            self.chart_panel.setVisible(not topo)
        if hasattr(self, 'chart3d'):
            self.chart3d.setVisible(topo)

    # ── Session REST ──

    def _start_session(self):
        self.lbl_info.setText("EEG : démarrage de la session…")
        req = QNetworkRequest(QUrl(f"{API_BASE}/acquisition/start"))
        req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        reply = self._nam.post(req, b"{}")
        reply.finished.connect(lambda: self._on_session_started(reply))

    def _on_session_started(self, reply: QNetworkReply):
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.lbl_info.setText(f"EEG : impossible de créer la session ({reply.errorString()})")
            self.lbl_info.setStyleSheet("color: #EF4444; font-size: 12px;")
            reply.deleteLater()
            return
        data = json.loads(reply.readAll().data())
        self.session_id = data.get("session_id")
        reply.deleteLater()
        self.ws.open(QUrl(f"{WS_BASE}/eeg/stream?session_id={self.session_id}"))

    def _stop_session(self):
        if not self.session_id:
            return
        req = QNetworkRequest(QUrl(f"{API_BASE}/acquisition/stop"))
        req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        body = json.dumps({"session_id": self.session_id}).encode()
        self._nam.post(req, body)

    # ── WebSocket ──

    def _on_ws_connected(self):
        self.lbl_info.setText("EEG : connecté")
        self.lbl_info.setStyleSheet("color: #22C55E; font-size: 12px;")

    def _on_ws_disconnected(self):
        self.lbl_info.setText("EEG : déconnecté")
        self.lbl_info.setStyleSheet("color: #6B7280; font-size: 12px;")

    def _on_ws_error(self, err):
        self.lbl_info.setText(f"EEG : erreur ({err})")
        self.lbl_info.setStyleSheet("color: #EF4444; font-size: 12px;")

    def _on_ws_msg(self, msg: str):
        if self.paused:
            return
        data = json.loads(msg)
        if "error" in data:
            self.lbl_info.setText(f"EEG : {data['error']}")
            return

        fatigue  = int(data.get("fatigue", 0))
        sfreq    = float(data.get("sfreq", 0.0))
        channels = data.get("channels", [])
        samples  = data.get("samples", [])
        t0       = float(data.get("t0", 0.0))
        alerts   = data.get("alerts", [])

        # Mise à jour fatigue UI
        self.lbl_fatigue.setText(f"{fatigue} / 100")
        self.bar.setValue(fatigue)

        if fatigue < 40:
            color = "#22C55E"
            status = "Alerte — OK"
        elif fatigue < 70:
            color = "#F59E0B"
            status = "Attention"
        else:
            color = "#EF4444"
            status = "Fatigue élevée"

        self.lbl_fatigue.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {color};")
        self.bar.setStyleSheet(f"""
            QProgressBar {{ background: #E5E7EB; border-radius: 5px; border: none; }}
            QProgressBar::chunk {{ background: {color}; border-radius: 5px; }}
        """)
        self.lbl_status.setText(status)

        # Alertes
        self.lbl_alerts.setText("\n".join(map(str, alerts)) if alerts else "Aucune alerte")

        # Chunk info
        n_ch   = len(samples)
        n_samp = len(samples[0]) if n_ch else 0
        self.lbl_chunk.setText(f"t0={t0:.2f}s  |  {n_ch} canaux  |  {n_samp} samples")

        # Mise à jour Three.js
        if self._topo_mode and hasattr(self, 'chart3d'):
            self.chart3d.add_samples(channels, samples, t0, sfreq)
        else:
            for elec in self.active_electrodes:
                self.brain.set_electrode_score(elec, fatigue)

        # Buffers
        if self.sfreq != sfreq or self.channels != channels or self.x is None:
            self._init_buffers(sfreq, channels)
        self._push_chunk(samples)

    # ── Three.js bridge ──

    def _on_electrodes_changed(self, active: list):
        self.active_electrodes = active
        if active:
            self.lbl_electrodes.setText("Actives : " + ", ".join(active))
        else:
            self.lbl_electrodes.setText("Aucune électrode sélectionnée")

    # ── Ring buffer ──

    def _init_buffers(self, sfreq, channels):
        self.sfreq    = sfreq
        self.channels = list(channels)
        self.max_samples = max(int(self.window_seconds * self.sfreq), 200)
        self.x = np.zeros((self.max_samples,), dtype=np.float32)
        self.y = np.zeros((len(self.channels), self.max_samples), dtype=np.float32)
        self.write_idx = self.count = 0
        self.t = 0.0
        self.plot.clear()
        self.plot.addLegend(offset=(10, 10))
        self.curves = [self.plot.plot([], [], name=ch) for ch in self.channels]

    def _push_chunk(self, samples_2d):
        if not samples_2d or self.y is None:
            return
        n_ch   = min(len(samples_2d), self.y.shape[0])
        n_samp = len(samples_2d[0]) if n_ch else 0
        if n_samp == 0:
            return
        dt      = 1.0 / float(self.sfreq)
        t_chunk = self.t + dt * (np.arange(n_samp, dtype=np.float32) + 1.0)
        self.t  = float(t_chunk[-1])
        w, end  = self.write_idx, self.write_idx + n_samp
        if end <= self.max_samples:
            self.x[w:end] = t_chunk
            for c in range(n_ch):
                self.y[c, w:end] = np.asarray(samples_2d[c], dtype=np.float32)
        else:
            f = self.max_samples - w
            self.x[w:] = t_chunk[:f];  self.x[:n_samp-f] = t_chunk[f:]
            for c in range(n_ch):
                arr = np.asarray(samples_2d[c], dtype=np.float32)
                self.y[c, w:] = arr[:f]; self.y[c, :n_samp-f] = arr[f:]
        self.write_idx = (w + n_samp) % self.max_samples
        self.count     = min(self.max_samples, self.count + n_samp)

    def _get_view(self):
        if self.count == 0 or self.x is None:
            return None, None
        n, w    = self.count, self.write_idx
        start   = (w - n) % self.max_samples
        if start < w:
            return self.x[start:w], self.y[:, start:w]
        return (np.concatenate([self.x[start:], self.x[:w]]),
                np.concatenate([self.y[:, start:], self.y[:, :w]], axis=1))

    # ── Rendu ──

    def _render(self):
        if self.paused or self.x is None or not self.curves:
            return
        x_view, y_view = self._get_view()
        if x_view is None:
            return
        m = x_view.shape[0]
        if m > 2000:
            step  = max(1, m // 2000)
            x_plot = x_view[::step];  y_plot = y_view[:, ::step]
        else:
            x_plot = x_view;          y_plot = y_view
        for i, curve in enumerate(self.curves):
            curve.setData(x_plot, y_plot[i])
        if x_plot.size > 2:
            self.plot.setXRange(float(x_plot[-1] - self.window_seconds), float(x_plot[-1]), padding=0)

    # ── Boutons ──

    def _toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.setText("Reprendre" if self.paused else "Pause")

    def _stop(self):
        self._stop_session()
        try:
            self.ws.close()
        except Exception:
            pass
        if self.on_stop:
            self.on_stop()
