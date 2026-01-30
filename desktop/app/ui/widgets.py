from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt

class Card(QFrame):
    def __init__(self, title: str | None = None):
        super().__init__()
        self.setObjectName("CardFrame")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 14, 16, 14)
        self.layout.setSpacing(10)

        if title:
            t = QLabel(title)
            t.setStyleSheet("font-size: 16px; font-weight: 600;")
            self.layout.addWidget(t)

class PageHeader(QWidget):
    def __init__(self, title: str, action_text: str | None = None, on_action=None):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        t = QLabel(title)
        t.setStyleSheet("font-size: 20px; font-weight: 600;")
        row.addWidget(t)

        row.addStretch(1)

        self.action_btn = None
        if action_text:
            b = QPushButton(action_text)
            b.setObjectName("PrimaryButton")
            b.setCursor(Qt.PointingHandCursor)
            if on_action:
                b.clicked.connect(on_action)
            row.addWidget(b)
            self.action_btn = b

def primary_button(text: str, on_click=None) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("PrimaryButton")
    b.setCursor(Qt.PointingHandCursor)
    if on_click:
        b.clicked.connect(on_click)
    return b

def secondary_button(text: str, on_click=None) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("SecondaryButton")
    b.setCursor(Qt.PointingHandCursor)
    if on_click:
        b.clicked.connect(on_click)
    return b

def danger_button(text: str, on_click=None) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("DangerButton")
    b.setCursor(Qt.PointingHandCursor)
    if on_click:
        b.clicked.connect(on_click)
    return b
