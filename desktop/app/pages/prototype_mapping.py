from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QCheckBox
from app.ui.widgets import Card, PageHeader, secondary_button

class PrototypeMappingPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Mapping commandes mentales → appareil (Prototype)"))

        warn = QLabel("Prototype — Contrôle d’un appareil externe (non homologué)")
        warn.setStyleSheet("color:#DC2626; font-weight: 600;")
        root.addWidget(warn)

        # Appareil externe
        c1 = Card("Appareil externe")
        g = QGridLayout()
        g.setHorizontalSpacing(14)
        g.setVerticalSpacing(10)

        lab = QLabel("Appareil")
        lab.setStyleSheet("color:#6B7280;")
        g.addWidget(lab, 0, 0)
        g.addWidget(QLineEdit(), 0, 1)

        st = QLabel("Statut : ○ Non connecté")
        st.setStyleSheet("color:#6B7280;")
        g.addWidget(st, 0, 2)

        btn = secondary_button("Tester la connexion")
        g.addWidget(btn, 0, 3)

        c1.layout.addLayout(g)
        root.addWidget(c1)

        # Mapping table
        c2 = Card("Mapping commandes mentales → actions")
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["Commande mentale", "Action sur l’appareil", "Test"])
        table.verticalHeader().setVisible(False)

        rows = ["Commande 1", "Commande 2", "Repos"]
        for i, r in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(r))
            table.setItem(i, 1, QTableWidgetItem("Choisir une action…"))
            play = QPushButton("▶")
            play.setObjectName("SecondaryButton")
            table.setCellWidget(i, 2, play)

        c2.layout.addWidget(table)
        root.addWidget(c2)

        # Mode simulation
        c3 = Card("Mode de fonctionnement")
        cb = QCheckBox("Mode simulation (aucun mouvement réel, feedback visuel uniquement)")
        c3.layout.addWidget(cb)
        dis = QLabel("Cette fonctionnalité est expérimentale et ne constitue pas un dispositif médical certifié.")
        dis.setStyleSheet("color:#DC2626;")
        c3.layout.addWidget(dis)
        root.addWidget(c3, 1)
