from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QHBoxLayout
from app.ui.widgets import Card, PageHeader, secondary_button, primary_button

class AdminUserCreatePage(QWidget):
    def __init__(self, on_cancel=None):
        super().__init__()
        self.on_cancel = on_cancel

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Administration — Nouvel utilisateur"))

        card = Card("Créer un utilisateur")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        def row(r, label):
            lab = QLabel(label)
            lab.setStyleSheet("color:#6B7280;")
            grid.addWidget(lab, r, 0)
            grid.addWidget(QLineEdit(), r, 1)

        row(0, "Nom")
        row(1, "Prénom")
        row(2, "Email / Login")
        row(3, "Mot de passe (init)")
        row(4, "Rôle")
        row(5, "Service")

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
