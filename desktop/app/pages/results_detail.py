from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from app.ui.widgets import Card, PageHeader, primary_button, secondary_button

class ResultsDetailPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Séance #123 — Résultats"))

        title = QLabel("Alice Dupont — Séance du 03/12/2025")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        root.addWidget(title)

        info = Card("Informations générales")
        info.layout.addWidget(QLabel(
            "Date / heure : 03/12/2025 — 10:12\nDurée : 15 minutes\nOpérateur : Infirmier(e) Martin\nDispositif : Casque EEG #1 | Protocole : Repos"
        ))
        root.addWidget(info)

        row = QHBoxLayout()
        row.setSpacing(14)

        indic = Card("Indicateurs de fatigue")
        indic.layout.addWidget(QLabel("Score moyen : 55 / 100\nScore maximum : 78 / 100\nSeuil critique : 70\nDépassement du seuil : Oui (3 fois)"))

        graphs = Card("Graphiques")
        graphs.layout.addWidget(QLabel("Score de fatigue / temps (placeholder)"))
        graphs.layout.addWidget(QLabel("Signal EEG (exemple) (placeholder)"))

        row.addWidget(indic, 1)
        row.addWidget(graphs, 1)
        root.addLayout(row)

        comm = Card("Commentaires")
        notes = QTextEdit()
        notes.setPlaceholderText("Notes du médecin…")
        notes.setFixedHeight(90)
        comm.layout.addWidget(notes)
        root.addWidget(comm)

        actions = QHBoxLayout()
        actions.addWidget(primary_button("Exporter en PDF"))
        actions.addWidget(secondary_button("Export CSV"))
        actions.addStretch(1)
        root.addLayout(actions)
