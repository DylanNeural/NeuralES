import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QFrame, QScrollArea
)
from app.ui.dialogs import InfoDialog
from PySide6.QtCore import Qt, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from app.ui.widgets import PageHeader, secondary_button, primary_button
import app.session as session

API_BASE = "http://127.0.0.1:8000"


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 2px;")
    return lbl


def _input(placeholder: str = "") -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setFixedHeight(38)
    w.setStyleSheet("""
        QLineEdit {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 0 12px;
            background: white;
            font-size: 13px;
            color: #111827;
        }
        QLineEdit:focus { border: 1px solid #2563EB; }
        QLineEdit:hover { border-color: #9CA3AF; }
    """)
    return w


def _combo(items: list) -> QComboBox:
    w = QComboBox()
    w.addItems(items)
    w.setFixedHeight(38)
    w.setStyleSheet("""
        QComboBox {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 0 12px;
            background: white;
            font-size: 13px;
            color: #111827;
        }
        QComboBox:focus { border: 1px solid #2563EB; }
        QComboBox::drop-down { border: none; width: 28px; }
        QComboBox::down-arrow { image: none; width: 0; }
    """)
    return w


class FormField(QVBoxLayout):
    def __init__(self, label: str, widget: QWidget):
        super().__init__()
        self.setSpacing(4)
        self.addWidget(_field_label(label))
        self.addWidget(widget)


class PatientCreatePage(QWidget):
    def __init__(self, on_cancel=None, on_saved=None):
        super().__init__()
        self.on_cancel = on_cancel
        self.on_saved  = on_saved
        self._nam = QNetworkAccessManager(self)
        self._edit_id = None   # None = création, int = édition

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Zone scrollable ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: #F3F4F6;")

        content = QWidget()
        content.setStyleSheet("background: #F3F4F6;")
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 22, 28, 28)
        root.setSpacing(18)

        self._header = PageHeader("Nouveau patient")
        root.addWidget(self._header)

        self._sub = QLabel("Remplissez les informations pour créer un nouveau dossier patient.")
        sub = self._sub
        sub.setStyleSheet("color: #6B7280; font-size: 13px; margin-top: -8px;")
        root.addWidget(sub)

        # ── Section 1 : Informations personnelles ──
        card1 = QFrame()
        card1.setObjectName("CardFrame")
        c1l = QVBoxLayout(card1)
        c1l.setContentsMargins(22, 20, 22, 20)
        c1l.setSpacing(16)

        t1 = QLabel("Informations personnelles")
        t1.setStyleSheet("font-size: 15px; font-weight: 700; color: #111827;")
        c1l.addWidget(t1)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color: #E5E7EB;")
        c1l.addWidget(sep1)

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(16)
        grid1.setVerticalSpacing(14)

        self.f_nom    = _input("ex: Dupont")
        self.f_prenom = _input("ex: Alice")
        self.f_dob    = _input("JJ/MM/AAAA")
        self.f_sexe   = _combo(["— Sélectionner —", "Femme", "Homme", "Autre"])
        self.f_nss    = _input("ex: 1 85 03 75 123 456 78")

        grid1.addLayout(FormField("Nom *",               self.f_nom),    0, 0)
        grid1.addLayout(FormField("Prénom *",            self.f_prenom), 0, 1)
        grid1.addLayout(FormField("Date de naissance *", self.f_dob),    1, 0)
        grid1.addLayout(FormField("Sexe *",              self.f_sexe),   1, 1)
        grid1.addLayout(FormField("N° sécurité sociale", self.f_nss),    2, 0, 1, 2)

        c1l.addLayout(grid1)
        root.addWidget(card1)

        # ── Section 2 : Informations médicales ──
        card2 = QFrame()
        card2.setObjectName("CardFrame")
        c2l = QVBoxLayout(card2)
        c2l.setContentsMargins(22, 20, 22, 20)
        c2l.setSpacing(16)

        t2 = QLabel("Informations médicales")
        t2.setStyleSheet("font-size: 15px; font-weight: 700; color: #111827;")
        c2l.addWidget(t2)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #E5E7EB;")
        c2l.addWidget(sep2)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(16)
        grid2.setVerticalSpacing(14)

        self.f_service = _combo(["— Sélectionner —", "Neurologie", "Cardiologie", "Sommeil", "Médecine T."])
        self.f_medecin = _combo(["— Sélectionner —", "Dr Martin", "Dr Durand", "Dr Petit", "Dr Noel"])
        self.f_notes   = _input("Informations complémentaires...")

        grid2.addLayout(FormField("Service",            self.f_service), 0, 0)
        grid2.addLayout(FormField("Médecin référent",   self.f_medecin), 0, 1)
        grid2.addLayout(FormField("Notes cliniques",    self.f_notes),   1, 0, 1, 2)

        c2l.addLayout(grid2)

        rem_layout = QVBoxLayout()
        rem_layout.setSpacing(4)
        rem_layout.addWidget(_field_label("Remarques"))
        self.f_remarques = QTextEdit()
        self.f_remarques.setPlaceholderText("Observations, antécédents, notes particulières...")
        self.f_remarques.setFixedHeight(90)
        self.f_remarques.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px 12px;
                background: white;
                font-size: 13px;
                color: #111827;
            }
            QTextEdit:focus { border: 1px solid #2563EB; }
        """)
        # empêche le QTextEdit de voler les événements scroll de la page
        self.f_remarques.wheelEvent = lambda e: e.ignore()
        rem_layout.addWidget(self.f_remarques)
        c2l.addLayout(rem_layout)
        root.addWidget(card2)

        # ── Boutons à la fin du formulaire ──
        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(10)

        btn_cancel = secondary_button("Annuler", on_click=self._cancel)
        btn_cancel.setFixedHeight(40)
        btn_cancel.setMinimumWidth(110)

        self.btn_save = primary_button("Enregistrer le patient", on_click=self._save)
        self.btn_save.setFixedHeight(40)
        self.btn_save.setMinimumWidth(180)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover { background: #1D4ED8; }
            QPushButton:pressed { background: #1E40AF; }
            QPushButton:disabled { background: #93C5FD; }
        """)

        actions_bar.addStretch(1)
        actions_bar.addWidget(btn_cancel)
        actions_bar.addWidget(self.btn_save)
        root.addLayout(actions_bar)
        root.addSpacing(10)

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

    def load_patient(self, patient: dict):
        """Passe en mode édition avec les données du patient pré-remplies."""
        self._edit_id = patient.get("patient_id")
        self._header.findChild(QLabel).setText("Modifier le patient")
        self._sub.setText("Modifiez les informations du dossier patient.")
        self.btn_save.setText("Enregistrer les modifications")

        self.f_nom.setText(patient.get("nom") or "")
        self.f_prenom.setText(patient.get("prenom") or "")
        dob = patient.get("date_naissance")
        if dob:
            try:
                from datetime import datetime
                self.f_dob.setText(datetime.strptime(dob, "%Y-%m-%d").strftime("%d/%m/%Y"))
            except Exception:
                self.f_dob.setText(dob)
        else:
            self.f_dob.setText("")

        sexe_map = {"femme": 1, "homme": 2}
        self.f_sexe.setCurrentIndex(sexe_map.get(patient.get("sexe") or "", 0))
        self.f_nss.setText(patient.get("numero_securite_sociale") or "")

        service = patient.get("service") or ""
        idx = self.f_service.findText(service)
        self.f_service.setCurrentIndex(idx if idx >= 0 else 0)

        medecin = patient.get("medecin_referent") or ""
        idx = self.f_medecin.findText(medecin)
        self.f_medecin.setCurrentIndex(idx if idx >= 0 else 0)

        self.f_notes.setText(patient.get("notes") or "")
        self.f_remarques.setPlainText(patient.get("remarque") or "")

    def reset(self):
        """Repasse en mode création."""
        self._edit_id = None
        self._header.findChild(QLabel).setText("Nouveau patient")
        self._sub.setText("Remplissez les informations pour créer un nouveau dossier patient.")
        self.btn_save.setText("Enregistrer le patient")
        for w in [self.f_nom, self.f_prenom, self.f_dob, self.f_nss, self.f_notes]:
            w.clear()
        self.f_sexe.setCurrentIndex(0)
        self.f_service.setCurrentIndex(0)
        self.f_medecin.setCurrentIndex(0)
        self.f_remarques.clear()

    def _cancel(self):
        self.reset()
        if self.on_cancel:
            self.on_cancel()

    def _save(self):
        nom    = self.f_nom.text().strip()
        prenom = self.f_prenom.text().strip()
        if not nom or not prenom:
            InfoDialog(self, "Champs requis", "Le nom et le prénom sont obligatoires.", kind="error").exec()
            return

        # identifiant_interne auto-généré
        import uuid
        sexe_map = {"Femme": "femme", "Homme": "homme"}
        sexe_raw = self.f_sexe.currentText()

        payload = {
            "identifiant_interne": f"PAT-{uuid.uuid4().hex[:8].upper()}",
            "nom":    nom,
            "prenom": prenom,
        }
        if self.f_dob.text().strip() not in ("", "JJ/MM/AAAA"):
            try:
                from datetime import datetime
                dob = datetime.strptime(self.f_dob.text().strip(), "%d/%m/%Y").date().isoformat()
                payload["date_naissance"] = dob
            except ValueError:
                pass
        if sexe_raw in sexe_map:
            payload["sexe"] = sexe_map[sexe_raw]
        nss = self.f_nss.text().strip().replace(" ", "")
        if len(nss) == 13 and nss.isdigit():
            payload["numero_securite_sociale"] = nss
        if self.f_service.currentIndex() > 0:
            payload["service"] = self.f_service.currentText()
        if self.f_medecin.currentIndex() > 0:
            payload["medecin_referent"] = self.f_medecin.currentText()
        if self.f_notes.text().strip():
            payload["notes"] = self.f_notes.text().strip()
        if self.f_remarques.toPlainText().strip():
            payload["remarque"] = self.f_remarques.toPlainText().strip()

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Enregistrement...")

        token = session.get_token()
        if self._edit_id:
            url = f"{API_BASE}/patients/{self._edit_id}"
            # PUT n'a pas identifiant_interne
            payload.pop("identifiant_interne", None)
        else:
            url = f"{API_BASE}/patients"

        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        if token:
            req.setRawHeader(b"Authorization", f"Bearer {token}".encode())
        body = QByteArray(json.dumps(payload).encode())
        if self._edit_id:
            reply = self._nam.put(req, body)
        else:
            reply = self._nam.post(req, body)
        reply.finished.connect(lambda: self._on_save_reply(reply))

    def _on_save_reply(self, reply: QNetworkReply):
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Enregistrer le patient")

        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        data = reply.readAll().data()

        if status in (200, 201):
            msg = "Les modifications ont été enregistrées." if self._edit_id else "Le dossier patient a été créé."
            InfoDialog(self, "Succès", msg, kind="success").exec()
            self.reset()
            if self.on_saved:
                self.on_saved()
            elif self.on_cancel:
                self.on_cancel()
        else:
            try:
                detail = json.loads(data).get("detail", "Erreur inconnue")
            except Exception:
                detail = f"Erreur serveur ({status})"
            InfoDialog(self, "Erreur", f"Impossible de créer le patient :\n{detail}", kind="error").exec()
