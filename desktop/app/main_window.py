from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from app.ui.sidebar import Sidebar
from app.ui.topbar import TopBar

from app.pages.dashboard import DashboardPage
from app.pages.patients_list import PatientsListPage
from app.pages.patient_create import PatientCreatePage
from app.pages.patient_detail import PatientDetailPage

from app.pages.sessions_list import SessionsListPage
from app.pages.new_session import NewSessionPage

from app.pages.acquisition import AcquisitionPage

from app.pages.results_list import ResultsListPage
from app.pages.results_detail import ResultsDetailPage

from app.pages.admin_hub import AdminHubPage
from app.pages.admin_users_list import AdminUsersListPage
from app.pages.admin_user_create import AdminUserCreatePage
from app.pages.admin_devices_list import AdminDevicesListPage
from app.pages.admin_device_create import AdminDeviceCreatePage

from app.pages.prototype_mapping import PrototypeMappingPage


class MainWindow(QMainWindow):
    """
    Shell principal : Sidebar + TopBar + Stack pages
    """
    def __init__(self, user_display: str = "Utilisateur : Dr Dupont"):
        super().__init__()
        self.setWindowTitle("Neural ES")
        self.resize(1440, 850)

        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(on_navigate=self.navigate)
        layout.addWidget(self.sidebar)

        # Right pane (topbar + pages)
        right = QWidget()
        right.setObjectName("RightPane")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.topbar = TopBar(user_label=user_display)
        self.topbar.logout_clicked.connect(self._on_logout)
        right_layout.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentStack")
        right_layout.addWidget(self.stack, 1)

        layout.addWidget(right, 1)

        # Pages (ordre = index)
        self.pages = {}
        self._add_page("dashboard", DashboardPage())
        self._add_page("patients_list", PatientsListPage(on_open_patient=self._open_patient, on_new_patient=lambda: self.navigate("patient_create")))
        self._add_page("patient_create", PatientCreatePage(on_cancel=lambda: self.navigate("patients_list")))
        self._add_page("patient_detail", PatientDetailPage(on_new_session=lambda: self.navigate("new_session")))

        self._add_page("sessions_list", SessionsListPage(on_new_session=lambda: self.navigate("new_session")))
        self._add_page("new_session", NewSessionPage(on_cancel=lambda: self.navigate("sessions_list"), on_start=lambda: self.navigate("acquisition")))

        self._add_page("acquisition", AcquisitionPage(on_stop=lambda: self.navigate("results_detail")))

        self._add_page("results_list", ResultsListPage(on_open_result=lambda: self.navigate("results_detail")))
        self._add_page("results_detail", ResultsDetailPage())

        self._add_page("admin_hub", AdminHubPage(on_users=lambda: self.navigate("admin_users_list"), on_devices=lambda: self.navigate("admin_devices_list")))
        self._add_page("admin_users_list", AdminUsersListPage(on_new=lambda: self.navigate("admin_user_create")))
        self._add_page("admin_user_create", AdminUserCreatePage(on_cancel=lambda: self.navigate("admin_users_list")))
        self._add_page("admin_devices_list", AdminDevicesListPage(on_new=lambda: self.navigate("admin_device_create")))
        self._add_page("admin_device_create", AdminDeviceCreatePage(on_cancel=lambda: self.navigate("admin_devices_list")))

        self._add_page("prototype_mapping", PrototypeMappingPage())

        self.navigate("dashboard")

    def _add_page(self, route: str, widget):
        self.pages[route] = self.stack.count()
        self.stack.addWidget(widget)

    def navigate(self, route: str):
        if route not in self.pages:
            return
        self.stack.setCurrentIndex(self.pages[route])
        self.sidebar.set_active(route)

    def _open_patient(self):
        # démo : ouvre la fiche patient
        self.navigate("patient_detail")

    def _on_logout(self):
        # Ici tu brancheras ton vrai logout (token etc.)
        self.close()
