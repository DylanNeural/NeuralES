import json
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QUrl


class _Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, src):
        print(f"[Chart3D JS] {msg}  (line {line})")


class Chart3DView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        from app.ui.brain_view import _start_server
        port = _start_server()
        self.setPage(_Page(self))
        self.load(QUrl(f'http://127.0.0.1:{port}/chart3d.html'))

    def add_samples(self, channels: list, samples: list, t0: float, sfreq: float):
        payload = json.dumps({
            'channels': channels,
            'samples':  samples,
            't0':       t0,
            'sfreq':    sfreq,
        })
        # Passer l'objet JS directement (pas une string) pour éviter l'escaping
        self.page().runJavaScript(f"if(window.addSamples) addSamples({payload});")

    def clear(self):
        self.page().runJavaScript("if(window.clearChart) clearChart();")
