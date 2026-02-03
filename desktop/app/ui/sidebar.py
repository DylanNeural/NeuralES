from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class Sidebar(QFrame):
    def __init__(self, on_navigate):
        super().__init__()
        self.setObjectName("Sidebar")
        self.on_navigate = on_navigate
        self.buttons = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Neural ES")
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        # menu maquette
        self._add_btn(layout, "dashboard", "Tableau de bord")
        self._add_btn(layout, "patients_list", "Patients")
        self._add_btn(layout, "sessions_list", "Séances")
        self._add_btn(layout, "acquisition", "Acquisition")
        self._add_btn(layout, "results_list", "Résultats")
        self._add_btn(layout, "admin_hub", "Administration")
        self._add_btn(layout, "prototype_mapping", "Prototype (Phase 2)")

        layout.addStretch(1)

    def _add_btn(self, layout, route, text):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setObjectName("SidebarButton")
        b.clicked.connect(lambda: self.on_navigate(route))
        layout.addWidget(b)
        self.buttons[route] = b

    def set_active(self, route: str):
        for r, b in self.buttons.items():
            b.setProperty("active", r == route)
            b.style().unpolish(b)
            b.style().polish(b)
