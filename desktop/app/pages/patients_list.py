from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
from app.ui.widgets import Card, PageHeader

class PatientsListPage(QWidget):
    def __init__(self, on_open_patient=None, on_new_patient=None):
        super().__init__()
        self.on_open_patient = on_open_patient
        self.on_new_patient = on_new_patient

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Patients", action_text="Nouveau patient", on_action=self._new))

        # barre filtres
        bar = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText("Rechercher un patient...")
        search.setMinimumWidth(260)

        service = QComboBox()
        service.addItems(["Service : Tous", "Neurologie", "Cardiologie"])
        service.setMinimumWidth(180)

        med = QComboBox()
        med.addItems(["Médecin : Tous", "Dr Martin", "Dr Durand"])
        med.setMinimumWidth(180)

        bar.addWidget(search)
        bar.addWidget(service)
        bar.addWidget(med)
        bar.addStretch(1)
        root.addLayout(bar)

        # table
        card = Card()
        table = QTableWidget(3, 5)
        table.setHorizontalHeaderLabels(["Nom", "Prénom", "Date de naissance", "Service", "Médecin référent"])
        table.verticalHeader().setVisible(False)
        table.setItem(0, 0, QTableWidgetItem("Dupont"))
        table.setItem(0, 1, QTableWidgetItem("Alice"))
        table.setItem(0, 2, QTableWidgetItem("12/03/1985"))
        table.setItem(0, 3, QTableWidgetItem("Neurologie"))
        table.setItem(0, 4, QTableWidgetItem("Dr Martin"))

        table.setItem(1, 0, QTableWidgetItem("Martin"))
        table.setItem(1, 1, QTableWidgetItem("Paul"))
        table.setItem(1, 2, QTableWidgetItem("08/11/1990"))
        table.setItem(1, 3, QTableWidgetItem("Médecine T."))
        table.setItem(1, 4, QTableWidgetItem("Dr Durand"))

        table.setItem(2, 0, QTableWidgetItem("Durand"))
        table.setItem(2, 1, QTableWidgetItem("Sophie"))
        table.setItem(2, 2, QTableWidgetItem("01/01/1978"))
        table.setItem(2, 3, QTableWidgetItem("Cardiologie"))
        table.setItem(2, 4, QTableWidgetItem("Dr Petit"))

        table.cellDoubleClicked.connect(lambda *_: self._open())
        card.layout.addWidget(table)
        root.addWidget(card, 1)

    def _open(self):
        if self.on_open_patient:
            self.on_open_patient()

    def _new(self):
        if self.on_new_patient:
            self.on_new_patient()
