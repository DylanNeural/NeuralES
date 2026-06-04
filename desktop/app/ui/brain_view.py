import os
import json
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot, Signal, QUrl


class _DebugPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f"[BrainView JS] {message}  (line {line})")

_BASE      = os.path.dirname(os.path.abspath(__file__))
_RESOURCES = os.path.normpath(os.path.join(_BASE, '..', 'ressources'))
_PUBLIC    = os.path.normpath(os.path.join(_BASE, '..', '..', '..', 'neurales-web', 'public'))

_httpd       = None
_server_port = None


def _start_server() -> int:
    global _httpd, _server_port
    if _server_port is not None:
        return _server_port

    print(f"[BrainView] RESOURCES dir : {_RESOURCES}")
    print(f"[BrainView] PUBLIC dir    : {_PUBLIC}")
    print(f"[BrainView] brain.html exists : {os.path.isfile(os.path.join(_RESOURCES, 'brain.html'))}")

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            print(f"[BrainView HTTP] {fmt % args}")

        def translate_path(self, path):
            p = path.split('?')[0].lstrip('/')
            for base in [_RESOURCES, _PUBLIC]:
                full = os.path.normpath(os.path.join(base, p))
                if os.path.isfile(full):
                    return full
            return os.path.normpath(os.path.join(_RESOURCES, p))

    _httpd = socketserver.TCPServer(('127.0.0.1', 0), Handler)
    _httpd.allow_reuse_address = True
    _server_port = _httpd.server_address[1]
    threading.Thread(target=_httpd.serve_forever, daemon=True).start()
    print(f"[BrainView] Serveur local démarré sur http://127.0.0.1:{_server_port}")
    return _server_port


class _Bridge(QObject):
    electrodes_changed = Signal(list)

    @Slot(str)
    def on_electrode_click(self, payload: str):
        data = json.loads(payload)
        self.electrodes_changed.emit(data.get('active', []))


class BrainView(QWebEngineView):
    """
    Vue Three.js du casque EEG embarquée dans PySide6 via QWebEngineView.

    Signaux :
        electrodes_changed(list[str])  — liste des électrodes actives après un clic

    Méthodes :
        set_electrode_score(name, score)  — colorie une électrode selon son score 0-100
        select_electrode(name, on)        — sélectionne/désélectionne depuis Python
        clear_electrodes()                — réinitialise toutes les sélections
    """

    electrodes_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        port = _start_server()

        self.setPage(_DebugPage(self))

        self._bridge = _Bridge()
        self._bridge.electrodes_changed.connect(self.electrodes_changed)

        channel = QWebChannel(self.page())
        channel.registerObject('bridge', self._bridge)
        self.page().setWebChannel(channel)

        self.load(QUrl(f'http://127.0.0.1:{port}/brain.html'))

    def set_electrode_score(self, name: str, score: float):
        self.page().runJavaScript(
            f"if(window.setElectrodeScore) setElectrodeScore({json.dumps(name)},{score});"
        )

    def select_electrode(self, name: str, on: bool):
        self.page().runJavaScript(
            f"if(window.selectElectrode) selectElectrode({json.dumps(name)},{str(on).lower()});"
        )

    def clear_electrodes(self):
        self.page().runJavaScript("if(window.clearElectrodes) clearElectrodes();")
