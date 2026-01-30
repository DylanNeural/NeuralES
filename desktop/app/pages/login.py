from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PySide6.QtCore import Qt
from app.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neural ES — Connexion")
        self.resize(1200, 720)

        root = QWidget()
        root.setObjectName("RightPane")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("CardFrame")
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(22, 22, 22, 22)
        card_l.setSpacing(12)
        card.setFixedWidth(420)

        title = QLabel("Neural Es")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        subtitle = QLabel("Analyse de la fatigue mentale")
        subtitle.setStyleSheet("color:#6B7280;")
        card_l.addWidget(title)
        card_l.addWidget(subtitle)

        card_l.addSpacing(10)

        lab1 = QLabel("Identifiant")
        lab1.setStyleSheet("color:#6B7280;")
        self.user = QLineEdit()
        self.user.setPlaceholderText("")
        card_l.addWidget(lab1)
        card_l.addWidget(self.user)

        lab2 = QLabel("Mot de passe")
        lab2.setStyleSheet("color:#6B7280;")
        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.Password)
        card_l.addWidget(lab2)
        card_l.addWidget(self.pw)

        card_l.addSpacing(8)

        btn = QPushButton("Se connecter")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(self._login)
        card_l.addWidget(btn)

        link = QLabel("Mot de passe oublié ?")
        link.setStyleSheet("color:#2563EB;")
        card_l.addWidget(link)

        layout.addWidget(card, alignment=Qt.AlignCenter)

    def _login(self):
        # Démo : ouvre directement l’app
        self.main = MainWindow(user_display="Utilisateur : Dr Dupont")
        self.main.show()
        self.close()
