from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from app.ui.widgets import PageHeader, Card

class AdminDevicesListPage(QWidget):
    def __init__(self, on_new=None):
        super().__init__()
        self.on_new = on_new

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Administration — Dispositifs", action_text="Nouveau dispositif", on_action=self._new))

        card = Card("Dispositifs (capteurs & appareils externes)")
        table = QTableWidget(3, 5)
        table.setHorizontalHeaderLabels(["Nom", "Type", "Marque / modèle", "Mode connexion", "Statut"])
        table.verticalHeader().setVisible(False)

        table.setItem(0, 0, QTableWidgetItem("Casque EEG #1"))
        table.setItem(0, 1, QTableWidgetItem("Capteur"))
        table.setItem(0, 2, QTableWidgetItem("OpenBCI"))
        table.setItem(0, 3, QTableWidgetItem("USB"))
        table.setItem(0, 4, QTableWidgetItem("Connecté"))

        table.setItem(1, 0, QTableWidgetItem("Casque EEG #2"))
        table.setItem(1, 1, QTableWidgetItem("Capteur"))
        table.setItem(1, 2, QTableWidgetItem("OpenBCI"))
        table.setItem(1, 3, QTableWidgetItem("Bluetooth"))
        table.setItem(1, 4, QTableWidgetItem("Non détecté"))

        table.setItem(2, 0, QTableWidgetItem("Prothèse démo"))
        table.setItem(2, 1, QTableWidgetItem("Appareil externe"))
        table.setItem(2, 2, QTableWidgetItem("DemoHand v1"))
        table.setItem(2, 3, QTableWidgetItem("IP"))
        table.setItem(2, 4, QTableWidgetItem("Prototype"))

        card.layout.addWidget(table)
        root.addWidget(card, 1)

    def _new(self):
        if self.on_new:
            self.on_new()
