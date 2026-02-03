from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from app.ui.widgets import PageHeader, Card

class AdminUsersListPage(QWidget):
    def __init__(self, on_new=None):
        super().__init__()
        self.on_new = on_new

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Administration — Utilisateurs", action_text="Nouvel utilisateur", on_action=self._new))

        card = Card("Gestion des utilisateurs")
        table = QTableWidget(3, 5)
        table.setHorizontalHeaderLabels(["Nom", "Prénom", "Email", "Rôle", "Service"])
        table.verticalHeader().setVisible(False)

        table.setItem(0, 0, QTableWidgetItem("Martin"))
        table.setItem(0, 1, QTableWidgetItem("Julie"))
        table.setItem(0, 2, QTableWidgetItem("j.martin@hopital.fr"))
        table.setItem(0, 3, QTableWidgetItem("Médecin"))
        table.setItem(0, 4, QTableWidgetItem("Travail"))

        table.setItem(1, 0, QTableWidgetItem("Durand"))
        table.setItem(1, 1, QTableWidgetItem("Paul"))
        table.setItem(1, 2, QTableWidgetItem("p.durand@hopital.fr"))
        table.setItem(1, 3, QTableWidgetItem("Infirmier"))
        table.setItem(1, 4, QTableWidgetItem("Neuro"))

        table.setItem(2, 0, QTableWidgetItem("Admin"))
        table.setItem(2, 1, QTableWidgetItem("Système"))
        table.setItem(2, 2, QTableWidgetItem("admin@hopital.fr"))
        table.setItem(2, 3, QTableWidgetItem("Admin"))
        table.setItem(2, 4, QTableWidgetItem("-"))

        card.layout.addWidget(table)
        root.addWidget(card, 1)

    def _new(self):
        if self.on_new:
            self.on_new()
