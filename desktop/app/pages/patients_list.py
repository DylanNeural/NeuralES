import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QLabel, QFrame, QHeaderView, QAbstractItemView
)
from app.ui.dialogs import ConfirmDialog, InfoDialog
from PySide6.QtCore import Qt, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QColor
from app.ui.widgets import PageHeader, primary_button
import app.session as session

API_BASE = "http://127.0.0.1:8000"

SERVICE_COLORS = {
    "Neurologie":   ("#EDE9FE", "#7C3AED"),
    "Cardiologie":  ("#FEE2E2", "#DC2626"),
    "Sommeil":      ("#DBEAFE", "#2563EB"),
    "Médecine T.":  ("#D1FAE5", "#059669"),
}

AVATAR_COLORS = [
    ("#EDE9FE", "#7C3AED"),
    ("#DBEAFE", "#2563EB"),
    ("#D1FAE5", "#059669"),
    ("#FEF3C7", "#D97706"),
    ("#FCE7F3", "#DB2777"),
]


class AvatarLabel(QLabel):
    def __init__(self, initials: str, index: int):
        super().__init__(initials)
        bg, fg = AVATAR_COLORS[index % len(AVATAR_COLORS)]
        self.setFixedSize(36, 36)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            background: {bg}; color: {fg};
            border-radius: 18px; font-weight: 700; font-size: 13px;
        """)


class BadgeLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text or "—")
        bg, fg = SERVICE_COLORS.get(text or "", ("#F3F4F6", "#6B7280"))
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(f"""
            background: {bg}; color: {fg};
            border-radius: 10px; padding: 4px 14px;
            font-size: 12px; font-weight: 600;
        """)


class PatientsListPage(QWidget):
    def __init__(self, on_open_patient=None, on_new_patient=None, on_edit_patient=None):
        super().__init__()
        self.on_open_patient  = on_open_patient
        self.on_new_patient   = on_new_patient
        self.on_edit_patient  = on_edit_patient
        self._all_patients   = []
        self._nam = QNetworkAccessManager(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(16)

        root.addWidget(PageHeader("Patients", action_text="+ Nouveau patient", on_action=self._new))

        # ── Stats ──
        self._stat_total  = QLabel("—")
        self._stat_neuro  = QLabel("—")
        self._stat_cardio = QLabel("—")
        self._stat_autres = QLabel("—")

        stats = QHBoxLayout()
        stats.setSpacing(12)
        for lbl_widget, label, color in [
            (self._stat_total,  "Total patients", "#2563EB"),
            (self._stat_neuro,  "Neurologie",     "#7C3AED"),
            (self._stat_cardio, "Cardiologie",    "#DC2626"),
            (self._stat_autres, "Autres services","#059669"),
        ]:
            card = QFrame()
            card.setObjectName("CardFrame")
            card.setFixedHeight(64)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 0, 16, 0)
            lbl_widget.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {color};")
            sub = QLabel(label)
            sub.setStyleSheet("font-size: 12px; color: #6B7280;")
            vl = QVBoxLayout()
            vl.setSpacing(0)
            vl.addWidget(lbl_widget)
            vl.addWidget(sub)
            cl.addLayout(vl)
            stats.addWidget(card, 1)
        root.addLayout(stats)

        # ── Filtres ──
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Rechercher un patient...")
        self.search.setFixedHeight(38)
        self.search.setStyleSheet("""
            QLineEdit { border:1px solid #E5E7EB; border-radius:8px; padding:0 12px; background:white; font-size:13px; }
            QLineEdit:focus { border-color:#2563EB; }
        """)
        self.search.textChanged.connect(self._filter)

        self.combo_service = QComboBox()
        self.combo_service.addItem("Tous les services")
        self.combo_service.setFixedHeight(38)
        self.combo_service.setMinimumWidth(170)
        self.combo_service.currentTextChanged.connect(self._filter)

        self.combo_med = QComboBox()
        self.combo_med.addItem("Tous les médecins")
        self.combo_med.setFixedHeight(38)
        self.combo_med.setMinimumWidth(170)
        self.combo_med.currentTextChanged.connect(self._filter)

        filter_bar.addWidget(self.search, 1)
        filter_bar.addWidget(self.combo_service)
        filter_bar.addWidget(self.combo_med)
        root.addLayout(filter_bar)

        # ── Table ──
        table_card = QFrame()
        table_card.setObjectName("CardFrame")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["", "Patient", "Date de naissance", "Service", "Médecin référent", ""])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 62)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 155)
        self.table.setColumnWidth(4, 160)
        self.table.setColumnWidth(5, 220)
        self.table.setStyleSheet("""
            QTableWidget { border:none; background:white; outline:none; }
            QTableWidget::item { padding:0 8px; border-bottom:1px solid #F3F4F6; }
            QTableWidget::item:selected { background:#EFF6FF; color:#111827; }
            QHeaderView::section {
                background:#F9FAFB; color:#6B7280; font-weight:600; font-size:12px;
                padding:10px 8px; border:none; border-bottom:1px solid #E5E7EB;
            }
        """)
        self.table.cellDoubleClicked.connect(lambda *_: self._open())
        self.table.setCursor(Qt.PointingHandCursor)
        table_layout.addWidget(self.table)
        root.addWidget(table_card, 1)

        self._load()

    # ── Chargement API ──
    def _load(self):
        req = QNetworkRequest(QUrl(f"{API_BASE}/patients?limit=200"))
        token = session.get_token()
        if token:
            req.setRawHeader(b"Authorization", f"Bearer {token}".encode())
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_patients(reply))

    def _on_patients(self, reply: QNetworkReply):
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        data = reply.readAll().data()
        if status != 200:
            print(f"[Patients] erreur {status}: {data}")
            return

        patients = json.loads(data)
        self._all_patients = patients

        # Mise à jour des filtres
        services = sorted({p.get("service") or "" for p in patients if p.get("service")})
        medecins = sorted({p.get("medecin_referent") or "" for p in patients if p.get("medecin_referent")})

        self.combo_service.blockSignals(True)
        self.combo_service.clear()
        self.combo_service.addItem("Tous les services")
        self.combo_service.addItems(services)
        self.combo_service.blockSignals(False)

        self.combo_med.blockSignals(True)
        self.combo_med.clear()
        self.combo_med.addItem("Tous les médecins")
        self.combo_med.addItems(medecins)
        self.combo_med.blockSignals(False)

        self._update_stats(patients)
        self._populate(patients)

    def _update_stats(self, patients):
        total  = len(patients)
        neuro  = sum(1 for p in patients if p.get("service") == "Neurologie")
        cardio = sum(1 for p in patients if p.get("service") == "Cardiologie")
        autres = total - neuro - cardio
        self._stat_total.setText(str(total))
        self._stat_neuro.setText(str(neuro))
        self._stat_cardio.setText(str(cardio))
        self._stat_autres.setText(str(autres))

    def _populate(self, patients):
        self.table.setRowCount(len(patients))
        for i, p in enumerate(patients):
            self.table.setRowHeight(i, 56)
            nom    = p.get("nom", "")
            prenom = p.get("prenom", "")
            raw_dob = p.get("date_naissance")
            if raw_dob:
                try:
                    from datetime import datetime
                    dob = datetime.strptime(raw_dob, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    dob = raw_dob
            else:
                dob = "—"
            service = p.get("service") or "—"
            medecin = p.get("medecin_referent") or "—"
            sexe    = p.get("sexe") or ""

            # Avatar
            initials = f"{prenom[:1]}{nom[:1]}".upper()
            avatar = AvatarLabel(initials, i)
            ctr = QWidget(); lay = QHBoxLayout(ctr)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setAlignment(Qt.AlignCenter)
            lay.addWidget(avatar)
            self.table.setCellWidget(i, 0, ctr)

            # Nom + genre
            name_w = QWidget(); nl = QVBoxLayout(name_w)
            nl.setContentsMargins(4, 0, 0, 0); nl.setSpacing(1)
            nl.addWidget(QLabel(f"{prenom} {nom}") if True else None)
            name_w.layout().itemAt(0).widget().setStyleSheet("font-weight:600; font-size:13px;")
            gender_map = {"homme": "Homme", "femme": "Femme"}
            genre_lbl = QLabel(gender_map.get(sexe, "—"))
            genre_lbl.setStyleSheet("font-size:11px; color:#9CA3AF;")
            nl.addWidget(genre_lbl)
            self.table.setCellWidget(i, 1, name_w)

            # DOB
            dob_item = QTableWidgetItem(dob)
            dob_item.setForeground(QColor("#374151"))
            self.table.setItem(i, 2, dob_item)

            # Badge service
            badge_ctr = QWidget(); bl = QHBoxLayout(badge_ctr)
            bl.setContentsMargins(8, 0, 8, 0)
            bl.addWidget(BadgeLabel(service if service != "—" else ""))
            bl.addStretch()
            self.table.setCellWidget(i, 3, badge_ctr)

            # Médecin
            med_item = QTableWidgetItem(medecin)
            med_item.setForeground(QColor("#374151"))
            self.table.setItem(i, 4, med_item)

            # Boutons actions
            btn_voir = primary_button("Voir", on_click=lambda _, pid=p["patient_id"]: self._open(pid))
            btn_voir.setFixedHeight(28); btn_voir.setMinimumWidth(50)
            btn_voir.setStyleSheet("""
                QPushButton { background:#EFF6FF; color:#2563EB; border:none; border-radius:6px; font-weight:600; font-size:11px; padding: 0 8px; }
                QPushButton:hover { background:#DBEAFE; }
            """)
            btn_edit = primary_button("Modifier", on_click=lambda _, row=p: self._edit(row))
            btn_edit.setFixedHeight(28); btn_edit.setMinimumWidth(65)
            btn_edit.setStyleSheet("""
                QPushButton { background:#F0FDF4; color:#059669; border:none; border-radius:6px; font-weight:600; font-size:11px; padding: 0 8px; }
                QPushButton:hover { background:#DCFCE7; }
            """)
            btn_del = primary_button("Supprimer", on_click=lambda _, pid=p["patient_id"], name=f"{prenom} {nom}": self._delete(pid, name))
            btn_del.setFixedHeight(28); btn_del.setMinimumWidth(75)
            btn_del.setStyleSheet("""
                QPushButton { background:#FEF2F2; color:#DC2626; border:none; border-radius:6px; font-weight:600; font-size:11px; padding: 0 8px; }
                QPushButton:hover { background:#FEE2E2; }
            """)
            btn_ctr = QWidget(); btl = QHBoxLayout(btn_ctr)
            btl.setContentsMargins(4, 0, 6, 0); btl.setSpacing(4)
            btl.addWidget(btn_voir); btl.addWidget(btn_edit); btl.addWidget(btn_del)
            self.table.setCellWidget(i, 5, btn_ctr)

    def _filter(self):
        query   = self.search.text().lower()
        service = self.combo_service.currentText()
        medecin = self.combo_med.currentText()
        filtered = [
            p for p in self._all_patients
            if query in f"{p.get('nom','')} {p.get('prenom','')}".lower()
            and (service == "Tous les services" or p.get("service") == service)
            and (medecin == "Tous les médecins" or p.get("medecin_referent") == medecin)
        ]
        self._populate(filtered)

    # Recharge les patients quand on revient sur la page (après création)
    def showEvent(self, event):
        super().showEvent(event)
        self._load()

    def _open(self, patient_id=None):
        if self.on_open_patient:
            self.on_open_patient(patient_id)

    def _edit(self, patient: dict):
        if self.on_edit_patient:
            self.on_edit_patient(patient)

    def _delete(self, patient_id: int, name: str):
        dlg = ConfirmDialog(
            self, "Confirmer la suppression",
            f"Supprimer le dossier de {name} ?\nCette action est irréversible.",
            confirm_text="Supprimer", danger=True
        )
        dlg.exec()
        if not dlg.confirmed():
            return

        req = QNetworkRequest(QUrl(f"{API_BASE}/patients/{patient_id}"))
        token = session.get_token()
        if token:
            req.setRawHeader(b"Authorization", f"Bearer {token}".encode())
        r = self._nam.deleteResource(req)
        r.finished.connect(lambda: self._on_deleted(r, name))

    def _on_deleted(self, reply: QNetworkReply, name: str):
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if status == 204:
            self._load()
        else:
            InfoDialog(self, "Erreur", f"Impossible de supprimer le patient ({status}).", kind="error").exec()

    def _new(self):
        if self.on_new_patient:
            self.on_new_patient()
