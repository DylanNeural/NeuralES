import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QColor
from app.ui.widgets import secondary_button, primary_button
import app.session as session

API_BASE = "http://127.0.0.1:8000"

AVATAR_COLORS = [
    ("#EDE9FE", "#7C3AED"), ("#DBEAFE", "#2563EB"), ("#D1FAE5", "#059669"),
    ("#FEF3C7", "#D97706"), ("#FCE7F3", "#DB2777"),
]
SERVICE_COLORS = {
    "Neurologie":  ("#EDE9FE", "#7C3AED"),
    "Cardiologie": ("#FEE2E2", "#DC2626"),
    "Sommeil":     ("#DBEAFE", "#2563EB"),
    "Médecine T.": ("#D1FAE5", "#059669"),
}


def _card(title=None):
    frame = QFrame()
    frame.setObjectName("CardFrame")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    if title:
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #111827;")
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E5E7EB;")
        layout.addWidget(lbl)
        layout.addWidget(sep)
    return frame, layout


def _info_row(label, value):
    row = QHBoxLayout()
    row.setSpacing(8)
    lbl = QLabel(label)
    lbl.setStyleSheet("font-size: 12px; color: #6B7280; min-width: 140px;")
    lbl.setFixedWidth(160)
    val = QLabel(value or "—")
    val.setStyleSheet("font-size: 13px; color: #111827; font-weight: 500;")
    val.setWordWrap(True)
    row.addWidget(lbl)
    row.addWidget(val, 1)
    return row


class PatientDetailPage(QWidget):
    def __init__(self, on_new_session=None, on_back=None):
        super().__init__()
        self.on_new_session = on_new_session
        self.on_back = on_back
        self._patient_id = None
        self._patient = None
        self._nam = QNetworkAccessManager(self)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Barre de titre ──
        title_bar = QFrame()
        title_bar.setStyleSheet("background: white; border-bottom: 1px solid #E5E7EB;")
        title_bar.setFixedHeight(56)
        tbl = QHBoxLayout(title_bar)
        tbl.setContentsMargins(24, 0, 24, 0)

        btn_back = secondary_button("← Patients", on_click=self._go_back)
        btn_back.setFixedHeight(34)
        tbl.addWidget(btn_back)
        tbl.addSpacing(16)

        self._title_lbl = QLabel("Fiche patient")
        self._title_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #111827;")
        tbl.addWidget(self._title_lbl)
        tbl.addStretch()

        self._btn_session = primary_button("+ Nouvelle séance", on_click=self._new_session)
        self._btn_session.setFixedHeight(36)
        self._btn_session.setMinimumWidth(150)
        tbl.addWidget(self._btn_session)
        main.addWidget(title_bar)

        # ── Zone scrollable ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F3F4F6;")

        content = QWidget()
        content.setStyleSheet("background: #F3F4F6;")
        self._root = QVBoxLayout(content)
        self._root.setContentsMargins(28, 22, 28, 28)
        self._root.setSpacing(16)

        # Placeholder de chargement
        self._loading = QLabel("Chargement...")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setStyleSheet("color: #6B7280; font-size: 14px;")
        self._root.addWidget(self._loading)
        self._root.addStretch()

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

    def load_patient(self, patient_id: int):
        self._patient_id = patient_id
        self._clear_content()
        self._loading.show()

        req = QNetworkRequest(QUrl(f"{API_BASE}/patients/{patient_id}"))
        token = session.get_token()
        if token:
            req.setRawHeader(b"Authorization", f"Bearer {token}".encode())
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_patient(reply))

    def _on_patient(self, reply: QNetworkReply):
        self._loading.hide()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if status != 200:
            self._loading.setText("Impossible de charger le patient.")
            self._loading.show()
            return

        self._patient = json.loads(reply.readAll().data())
        self._build_ui()

    def _clear_content(self):
        while self._root.count() > 2:
            item = self._root.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _build_ui(self):
        p = self._patient
        nom    = p.get("nom", "")
        prenom = p.get("prenom", "")
        sexe_map = {"homme": "Homme", "femme": "Femme"}

        # Mettre à jour le titre
        self._title_lbl.setText(f"{prenom} {nom}")

        # ── En-tête patient ──
        header_card, hl = _card()
        header_row = QHBoxLayout()
        header_row.setSpacing(18)

        # Avatar grand
        initials = f"{prenom[:1]}{nom[:1]}".upper()
        bg, fg = AVATAR_COLORS[hash(nom) % len(AVATAR_COLORS)]
        avatar = QLabel(initials)
        avatar.setFixedSize(64, 64)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {bg}; color: {fg};
            border-radius: 32px; font-size: 22px; font-weight: 700;
        """)
        header_row.addWidget(avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_lbl = QLabel(f"{prenom} {nom}")
        name_lbl.setStyleSheet("font-size: 20px; font-weight: 700; color: #111827;")
        name_col.addWidget(name_lbl)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(8)
        if p.get("sexe"):
            sex_lbl = QLabel(sexe_map.get(p["sexe"], p["sexe"]))
            sex_lbl.setStyleSheet("font-size: 12px; color: #6B7280;")
            sub_row.addWidget(sex_lbl)
        if p.get("service"):
            bg_s, fg_s = SERVICE_COLORS.get(p["service"], ("#F3F4F6", "#6B7280"))
            badge = QLabel(p["service"])
            badge.setStyleSheet(f"""
                background: {bg_s}; color: {fg_s};
                border-radius: 10px; padding: 2px 10px;
                font-size: 12px; font-weight: 600;
            """)
            sub_row.addWidget(badge)
        sub_row.addStretch()
        name_col.addLayout(sub_row)
        header_row.addLayout(name_col, 1)

        id_lbl = QLabel(f"ID : {p.get('identifiant_interne', '—')}")
        id_lbl.setStyleSheet("font-size: 12px; color: #9CA3AF;")
        id_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_row.addWidget(id_lbl)

        hl.addLayout(header_row)
        self._root.insertWidget(self._root.count() - 1, header_card)

        # ── Ligne infos + médical ──
        cols = QHBoxLayout()
        cols.setSpacing(16)

        # Infos personnelles
        card1, l1 = _card("Informations personnelles")
        dob = p.get("date_naissance") or "—"
        nss = p.get("numero_securite_sociale") or "—"
        for label, val in [
            ("Nom",                  nom),
            ("Prénom",               prenom),
            ("Date de naissance",    dob),
            ("Sexe",                 sexe_map.get(p.get("sexe") or "", "—")),
            ("N° sécurité sociale",  nss),
        ]:
            l1.addLayout(_info_row(label, val))
        l1.addStretch()
        cols.addWidget(card1, 1)

        # Infos médicales
        card2, l2 = _card("Informations médicales")
        for label, val in [
            ("Service",         p.get("service") or "—"),
            ("Médecin référent", p.get("medecin_referent") or "—"),
            ("Notes cliniques",  p.get("notes") or "—"),
            ("Remarques",        p.get("remarque") or "—"),
        ]:
            l2.addLayout(_info_row(label, val))
        l2.addStretch()
        cols.addWidget(card2, 1)

        self._root.insertWidget(self._root.count() - 1, QWidget())  # spacer placeholder
        container = QWidget()
        container.setLayout(cols)
        self._root.insertWidget(self._root.count() - 1, container)

        # ── Historique des séances (mocké pour l'instant) ──
        card3, l3 = _card("Historique des séances")

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Date", "Durée", "Score fatigue", "Statut"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget { border: none; background: white; outline: none; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #F3F4F6; color: #374151; }
            QTableWidget::item:selected { background: #EFF6FF; color: #111827; }
            QHeaderView::section {
                background: #F9FAFB; color: #6B7280; font-weight: 600; font-size: 12px;
                padding: 8px; border: none; border-bottom: 1px solid #E5E7EB;
            }
        """)
        table.setFixedHeight(160)

        empty = QLabel("Aucune séance enregistrée pour ce patient.")
        empty.setAlignment(Qt.AlignCenter)
        empty.setStyleSheet("color: #9CA3AF; font-size: 13px; padding: 20px;")
        l3.addWidget(table)
        l3.addWidget(empty)
        self._root.insertWidget(self._root.count() - 1, card3)

    def _go_back(self):
        if self.on_back:
            self.on_back()

    def _new_session(self):
        if self.on_new_session:
            self.on_new_session()
