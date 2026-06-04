from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def _btn(text, bg, fg, hover):
    b = QPushButton(text)
    b.setFixedHeight(38)
    b.setMinimumWidth(100)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {fg};
            border: none; border-radius: 8px;
            font-size: 13px; font-weight: 600; padding: 0 20px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return b


class ConfirmDialog(QDialog):
    """Boîte de confirmation Oui / Non."""
    def __init__(self, parent, title: str, message: str, confirm_text="Confirmer", cancel_text="Annuler", danger=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._result = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                border: 1px solid #E5E7EB;
            }
        """)
        card.setMinimumWidth(420)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Icône + titre
        title_row = QHBoxLayout()
        icon = QLabel("🗑️" if danger else "❓")
        icon.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #111827; background: transparent; border: none;")
        title_row.addWidget(icon)
        title_row.addWidget(title_lbl, 1)
        layout.addLayout(title_row)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E5E7EB; background: #E5E7EB; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # Message
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size: 13px; color: #374151; background: transparent; border: none; line-height: 1.5;")
        layout.addWidget(msg_lbl)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_cancel = _btn(cancel_text, "#F3F4F6", "#374151", "#E5E7EB")
        btn_cancel.clicked.connect(self.reject)

        if danger:
            btn_ok = _btn(confirm_text, "#DC2626", "white", "#B91C1C")
        else:
            btn_ok = _btn(confirm_text, "#2563EB", "white", "#1D4ED8")
        btn_ok.clicked.connect(self._accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        outer.addWidget(card)

    def _accept(self):
        self._result = True
        self.accept()

    def confirmed(self) -> bool:
        return self._result


class InfoDialog(QDialog):
    """Boîte d'information / succès / erreur."""
    def __init__(self, parent, title: str, message: str, kind="success"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        icons   = {"success": "✅", "error": "❌", "info": "ℹ️"}
        colors  = {"success": "#059669", "error": "#DC2626", "info": "#2563EB"}
        bgs     = {"success": "#F0FDF4", "error": "#FEF2F2", "info": "#EFF6FF"}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border-radius: 14px; border: 1px solid #E5E7EB; }")
        card.setMinimumWidth(380)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Bandeau coloré en haut
        banner = QFrame()
        banner.setFixedHeight(6)
        banner.setStyleSheet(f"background: {colors[kind]}; border-radius: 3px; border: none;")
        layout.addWidget(banner)

        # Icône + titre
        title_row = QHBoxLayout()
        icon = QLabel(icons.get(kind, "ℹ️"))
        icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {colors[kind]}; background: transparent; border: none;")
        title_row.addWidget(icon)
        title_row.addWidget(title_lbl, 1)
        layout.addLayout(title_row)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size: 13px; color: #374151; background: transparent; border: none;")
        layout.addWidget(msg_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = _btn("OK", colors[kind], "white", colors[kind])
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        outer.addWidget(card)
