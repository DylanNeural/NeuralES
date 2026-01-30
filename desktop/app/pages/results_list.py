from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.ui.widgets import PageHeader, Card

class ResultsListPage(QWidget):
    def __init__(self, on_open_result=None):
        super().__init__()
        self.on_open_result = on_open_result

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Résultats"))
        card = Card()
        card.layout.addWidget(QLabel("Écran liste des résultats (placeholder).\nDouble-clique depuis une table plus tard, ou navigue vers le détail."))
        root.addWidget(card, 1)
