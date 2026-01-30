from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

class TopBar(QFrame):
    logout_clicked = Signal()

    def __init__(self, user_label: str):
        super().__init__()
        self.setObjectName("TopBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(12)

        layout.addStretch(1)

        user = QLabel(user_label)
        user.setObjectName("TopBarUser")
        layout.addWidget(user)

        btn = QPushButton("Déconnexion")
        btn.setObjectName("SecondaryButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(btn)
