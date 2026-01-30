from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
from app.ui.widgets import Card, PageHeader, secondary_button, primary_button

class NewSessionPage(QWidget):
    def __init__(self, on_cancel=None, on_start=None):
        super().__init__()
        self.on_cancel = on_cancel
        self.on_start = on_start

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Nouvelle séance"))

        # Patient
        c1 = Card("Patient")
        g1 = QGridLayout()
        g1.setVerticalSpacing(10)
        lab = QLabel("Sélectionner un patient")
        lab.setStyleSheet("color:#6B7280;")
        g1.addWidget(lab, 0, 0)
        g1.addWidget(QLineEdit(), 0, 1)
        c1.layout.addLayout(g1)

        # Dispositif de mesure
        c2 = Card("Dispositif de mesure")
        g2 = QGridLayout()
        g2.setVerticalSpacing(10)
        l1 = QLabel("Dispositif")
        l1.setStyleSheet("color:#6B7280;")
        g2.addWidget(l1, 0, 0)
        g2.addWidget(QLineEdit(), 0, 1)

        qual = QLabel("Qualité du signal : Bonne")
        qual.setStyleSheet("color:#16A34A;")
        g2.addWidget(qual, 1, 0)

        btn_test = QPushButton("Tester la connexion")
        btn_test.setObjectName("SecondaryButton")
        g2.addWidget(btn_test, 1, 1)
        c2.layout.addLayout(g2)

        # Paramètres de séance
        c3 = Card("Paramètres de la séance")
        g3 = QGridLayout()
        g3.setVerticalSpacing(10)

        def row(r, label):
            lab = QLabel(label)
            lab.setStyleSheet("color:#6B7280;")
            g3.addWidget(lab, r, 0)
            g3.addWidget(QLineEdit(), r, 1)

        row(0, "Type de protocole")
        row(1, "Durée (min)")
        row(2, "Fréquence d’échantillonnage")
        c3.layout.addLayout(g3)

        # Seuil fatigue
        c4 = Card("Seuil de fatigue")
        g4 = QGridLayout()
        g4.setVerticalSpacing(10)
        l = QLabel("Seuil critique (0-100)")
        l.setStyleSheet("color:#6B7280;")
        g4.addWidget(l, 0, 0)
        g4.addWidget(QLineEdit(), 0, 1)
        c4.layout.addLayout(g4)

        root.addWidget(c1)
        root.addWidget(c2)
        root.addWidget(c3)
        root.addWidget(c4, 1)

        actions = QHBoxLayout()
        actions.addWidget(secondary_button("Annuler", on_click=self._cancel))
        actions.addWidget(primary_button("Démarrer la séance", on_click=self._start))
        actions.addStretch(1)
        root.addLayout(actions)

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()

    def _start(self):
        if self.on_start:
            self.on_start()
