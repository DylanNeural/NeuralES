from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QHBoxLayout
from app.ui.widgets import Card, PageHeader, secondary_button, primary_button

class AdminDeviceCreatePage(QWidget):
    def __init__(self, on_cancel=None):
        super().__init__()
        self.on_cancel = on_cancel

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Administration — Dispositif"))

        card = Card("Nouveau dispositif")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        def row(r, label, placeholder=""):
            lab = QLabel(label)
            lab.setStyleSheet("color:#6B7280;")
            inp = QLineEdit()
            if placeholder:
                inp.setPlaceholderText(placeholder)
            grid.addWidget(lab, r, 0)
            grid.addWidget(inp, r, 1)

        row(0, "Nom")
        row(1, "Type (capteur / appareil externe)")
        row(2, "Marque / modèle")
        row(3, "Mode de connexion (USB, BT, IP)")
        row(4, "Configuration (adresse IP, port, etc.)")

        card.layout.addLayout(grid)

        actions = QHBoxLayout()
        actions.addWidget(secondary_button("Annuler", on_click=self._cancel))
        actions.addWidget(primary_button("Enregistrer"))
        actions.addStretch(1)
        card.layout.addLayout(actions)

        root.addWidget(card, 1)

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()
