from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from app.ui.widgets import Card, PageHeader

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Tableau de bord"))

        row = QHBoxLayout()
        row.setSpacing(14)

        c1 = Card("Patients récents")
        c1.layout.addWidget(QLabel("• Alice Dupont — 03/12/2025\n• Paul Martin — 02/12/2025"))

        c2 = Card("Séances récentes")
        c2.layout.addWidget(QLabel("• 03/12 — A. Dupont — Score max 78\n• 02/12 — P. Martin — Score max 60"))

        row.addWidget(c1, 1)
        row.addWidget(c2, 1)
        root.addLayout(row)

        c3 = Card("Statut des dispositifs")
        c3.layout.addWidget(QLabel("Casque EEG #1 — ● Connecté — Qualité : Bonne\nCasque EEG #2 — ○ Non détecté\nProthèse démo — ○ Non connecté (Prototype Phase 2)"))
        root.addWidget(c3, 1)
