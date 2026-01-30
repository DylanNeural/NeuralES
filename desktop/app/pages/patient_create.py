from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QHBoxLayout
from app.ui.widgets import Card, PageHeader, secondary_button, primary_button

class PatientCreatePage(QWidget):
    def __init__(self, on_cancel=None):
        super().__init__()
        self.on_cancel = on_cancel

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Nouveau patient"))

        card = Card("Créer une fiche patient")
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        def row(r, label, widget):
            lab = QLabel(label)
            lab.setStyleSheet("color:#6B7280;")
            grid.addWidget(lab, r, 0)
            grid.addWidget(widget, r, 1)

        row(0, "Nom", QLineEdit())
        row(1, "Prénom", QLineEdit())
        row(2, "Date de naissance", QLineEdit())
        row(3, "N° sécurité sociale", QLineEdit())
        row(4, "Sexe", QLineEdit())
        row(5, "Service", QLineEdit())
        row(6, "Médecin référent", QLineEdit())
        rem = QTextEdit()
        rem.setFixedHeight(80)
        row(7, "Remarques", rem)

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
