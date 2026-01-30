from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from app.ui.widgets import Card, PageHeader, secondary_button, primary_button

class PatientDetailPage(QWidget):
    def __init__(self, on_new_session=None):
        super().__init__()
        self.on_new_session = on_new_session

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Fiche patient"))

        name = QLabel("Alice Dupont")
        name.setStyleSheet("font-size: 20px; font-weight: 600;")
        root.addWidget(name)

        row = QHBoxLayout()
        row.setSpacing(14)

        info = Card("Informations patient")
        info.layout.addWidget(QLabel(
            "Nom : Dupont\nPrénom : Alice\nDate de naissance : 12/03/1985\n"
            "N° sécurité sociale : XXX-XX-XXXX\nSexe : F\nService : Neurologie\n"
            "Médecin référent : Dr Martin\nRemarques : …"
        ))
        btns = QHBoxLayout()
        btns.addWidget(secondary_button("Modifier"))
        btns.addWidget(secondary_button("Archiver"))
        btns.addStretch(1)
        info.layout.addLayout(btns)

        hist = Card("Historique des séances")
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["Date", "Score max", "Seuil dépassé"])
        table.verticalHeader().setVisible(False)
        table.setItem(0, 0, QTableWidgetItem("03/12/2025"))
        table.setItem(0, 1, QTableWidgetItem("78"))
        table.setItem(0, 2, QTableWidgetItem("Oui"))
        table.setItem(1, 0, QTableWidgetItem("01/12/2025"))
        table.setItem(1, 1, QTableWidgetItem("45"))
        table.setItem(1, 2, QTableWidgetItem("Non"))
        table.setItem(2, 0, QTableWidgetItem("25/11/2025"))
        table.setItem(2, 1, QTableWidgetItem("60"))
        table.setItem(2, 2, QTableWidgetItem("Oui"))
        hist.layout.addWidget(table)

        row.addWidget(info, 1)
        row.addWidget(hist, 1)
        root.addLayout(row)

        root.addWidget(primary_button("Nouvelle séance pour ce patient", on_click=self._new_session), 0)

    def _new_session(self):
        if self.on_new_session:
            self.on_new_session()
