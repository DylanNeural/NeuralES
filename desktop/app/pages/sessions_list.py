from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.ui.widgets import PageHeader, Card

class SessionsListPage(QWidget):
    def __init__(self, on_new_session=None):
        super().__init__()
        self.on_new_session = on_new_session

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Séances", action_text="Nouvelle séance", on_action=self._new))
        card = Card()
        card.layout.addWidget(QLabel("Écran liste des séances (placeholder)\nTu peux l’ajouter si besoin."))
        root.addWidget(card, 1)

    def _new(self):
        if self.on_new_session:
            self.on_new_session()
