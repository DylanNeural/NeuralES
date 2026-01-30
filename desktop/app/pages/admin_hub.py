from PySide6.QtWidgets import QWidget, QVBoxLayout
from app.ui.widgets import PageHeader, Card, primary_button

class AdminHubPage(QWidget):
    def __init__(self, on_users=None, on_devices=None):
        super().__init__()
        self.on_users = on_users
        self.on_devices = on_devices

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        root.addWidget(PageHeader("Administration"))

        c = Card("Choisir une section")
        c.layout.addWidget(primary_button("Gestion des utilisateurs", on_click=lambda: self.on_users() if self.on_users else None))
        c.layout.addWidget(primary_button("Gestion des dispositifs", on_click=lambda: self.on_devices() if self.on_devices else None))
        root.addWidget(c, 1)
