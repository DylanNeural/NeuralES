import json
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PySide6.QtCore import Qt, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QByteArray
from app.main_window import MainWindow
import app.session as session

API_BASE = "http://127.0.0.1:8000"


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neural ES — Connexion")
        self.resize(1200, 720)
        self._nam = QNetworkAccessManager(self)

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
        self.user.setText("admin@neurales.com")
        self.user.setPlaceholderText("email@exemple.com")
        card_l.addWidget(lab1)
        card_l.addWidget(self.user)

        lab2 = QLabel("Mot de passe")
        lab2.setStyleSheet("color:#6B7280;")
        self.pw = QLineEdit()
        self.pw.setText("Admin1234")
        self.pw.setEchoMode(QLineEdit.Password)
        self.pw.returnPressed.connect(self._login)
        card_l.addWidget(lab2)
        card_l.addWidget(self.pw)

        card_l.addSpacing(8)

        self.btn = QPushButton("Se connecter")
        self.btn.setObjectName("PrimaryButton")
        self.btn.clicked.connect(self._login)
        card_l.addWidget(self.btn)

        self.err_label = QLabel("")
        self.err_label.setStyleSheet("color:#EF4444; font-size:12px;")
        self.err_label.setAlignment(Qt.AlignCenter)
        card_l.addWidget(self.err_label)

        layout.addWidget(card, alignment=Qt.AlignCenter)

    def _login(self):
        email = self.user.text().strip()
        password = self.pw.text()
        if not email or not password:
            self.err_label.setText("Veuillez remplir tous les champs.")
            return

        self.btn.setText("Connexion...")
        self.btn.setEnabled(False)
        self.err_label.setText("")

        req = QNetworkRequest(QUrl(f"{API_BASE}/auth/login"))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        body = QByteArray(json.dumps({"email": email, "password": password}).encode())
        reply = self._nam.post(req, body)
        reply.finished.connect(lambda: self._on_login_reply(reply))

    def _on_login_reply(self, reply: QNetworkReply):
        self.btn.setText("Se connecter")
        self.btn.setEnabled(True)

        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        data = reply.readAll().data()

        if status == 200:
            token = json.loads(data).get("access_token", "")
            session.set_token(token)
            email_prefix = self.user.text().split("@")[0].capitalize()
            self.main = MainWindow(user_display=f"Dr {email_prefix}")
            self.main.show()
            self.close()
        else:
            try:
                detail = json.loads(data).get("detail", "Erreur inconnue")
            except Exception:
                detail = f"Erreur serveur ({status})"
            self.err_label.setText(f"Échec : {detail}")
