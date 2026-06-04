import json
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QColor, QLinearGradient, QPalette, QFont
import app.session as session

API_BASE = "http://127.0.0.1:8000"

JOURS  = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
MOIS   = ["janvier","février","mars","avril","mai","juin",
          "juillet","août","septembre","octobre","novembre","décembre"]

AVATAR_COLORS = [
    ("#EDE9FE","#7C3AED"), ("#DBEAFE","#2563EB"), ("#D1FAE5","#059669"),
    ("#FEF3C7","#D97706"), ("#FCE7F3","#DB2777"),
]


def _shadow(widget, blur=18, offset_y=4, color="#00000015"):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset_y)
    fx.setColor(QColor(color))
    widget.setGraphicsEffect(fx)
    return widget


def _vline(color="#E5E7EB"):
    f = QFrame(); f.setFrameShape(QFrame.VLine)
    f.setStyleSheet(f"color: {color};"); f.setFixedWidth(1)
    return f


class KpiCard(QFrame):
    def __init__(self, icon, value, label, sub, color, bg_light):
        super().__init__()
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
                border: 1.5px solid #F1F5F9;
            }}
        """)
        _shadow(self, blur=20, offset_y=3, color="#0000000D")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(16)

        # Icône
        icon_box = QLabel(icon)
        icon_box.setFixedSize(48, 48)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: {bg_light};
            border-radius: 14px;
            font-size: 20px;
        """)
        lay.addWidget(icon_box)

        # Texte
        col = QVBoxLayout()
        col.setSpacing(2)
        col.setAlignment(Qt.AlignVCenter)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {color};")

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #374151;")

        sub_lbl = QLabel(sub)
        sub_lbl.setStyleSheet("font-size: 11px; color: #9CA3AF;")

        col.addWidget(self.val_lbl)
        col.addWidget(lbl)
        col.addWidget(sub_lbl)
        lay.addLayout(col, 1)

        # Accent bar droite
        bar = QFrame()
        bar.setFixedSize(4, 52)
        bar.setStyleSheet(f"background: {color}; border-radius: 2px; border: none;")
        lay.addWidget(bar)


class PatientItem(QFrame):
    def __init__(self, p: dict, idx: int):
        super().__init__()
        nom    = p.get("nom","")
        prenom = p.get("prenom","")
        svc    = p.get("service") or "—"
        dob    = p.get("date_naissance") or ""
        if dob:
            try: dob = datetime.strptime(dob, "%Y-%m-%d").strftime("%d/%m/%Y")
            except: pass

        self.setStyleSheet("""
            QFrame { background: transparent; border-radius: 10px; }
            QFrame:hover { background: #F8FAFC; }
        """)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)

        bg, fg = AVATAR_COLORS[hash(nom) % len(AVATAR_COLORS)]
        av = QLabel(f"{prenom[:1]}{nom[:1]}".upper())
        av.setFixedSize(38, 38)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background:{bg}; color:{fg}; border-radius:19px; font-weight:700; font-size:13px;")
        lay.addWidget(av)

        info = QVBoxLayout(); info.setSpacing(1)
        n = QLabel(f"{prenom} {nom}")
        n.setStyleSheet("font-size: 13px; font-weight: 600; color: #111827;")
        s = QLabel(svc)
        s.setStyleSheet("font-size: 11px; color: #6B7280;")
        info.addWidget(n); info.addWidget(s)
        lay.addLayout(info, 1)

        dob_lbl = QLabel(dob)
        dob_lbl.setStyleSheet("font-size: 11px; color: #9CA3AF;")
        lay.addWidget(dob_lbl)


class QuickBtn(QFrame):
    def __init__(self, icon, label, color):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1.5px solid #F1F5F9;
            }}
            QFrame:hover {{
                border: 1.5px solid {color};
                background: #FAFBFF;
            }}
        """)
        _shadow(self, blur=12, offset_y=2, color="#0000000A")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        ic = QLabel(icon)
        ic.setStyleSheet("font-size: 18px; background: transparent;")
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: #374151; background: transparent;")
        arr = QLabel("→")
        arr.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: 700; background: transparent;")

        lay.addWidget(ic); lay.addWidget(lbl, 1); lay.addWidget(arr)


class DeviceItem(QFrame):
    def __init__(self, name, online, detail=None):
        super().__init__()
        self.setFixedHeight(48)
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(10)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        c = "#10B981" if online else "#E5E7EB"
        dot.setStyleSheet(f"background:{c}; border-radius:4px; border:none;")
        lay.addWidget(dot)

        n = QLabel(name)
        n.setStyleSheet("font-size: 13px; color: #374151; font-weight: 500;")
        lay.addWidget(n, 1)

        st = QLabel("En ligne" if online else "Non détecté")
        col = "#10B981" if online else "#9CA3AF"
        st.setStyleSheet(f"font-size: 11px; color: {col}; font-weight: 600;")
        lay.addWidget(st)


def _card_title(text, color="#2563EB"):
    w = QLabel(text)
    w.setStyleSheet(f"font-size: 13px; font-weight: 700; color: #111827; padding: 16px 16px 0 16px;")
    return w


def _hdivider():
    f = QFrame(); f.setFrameShape(QFrame.HLine)
    f.setStyleSheet("color: #F1F5F9; background: #F1F5F9; max-height:1px; border:none; margin: 4px 16px;")
    return f


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._nam = QNetworkAccessManager(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #F8FAFC;")

        content = QWidget()
        content.setStyleSheet("background: #F8FAFC;")
        root = QVBoxLayout(content)
        root.setContentsMargins(32, 28, 32, 32)
        root.setSpacing(24)

        # ── Hero ──
        hero = QFrame()
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E40AF, stop:0.5 #2563EB, stop:1 #7C3AED);
                border-radius: 20px;
            }
        """)
        hero.setFixedHeight(110)
        _shadow(hero, blur=24, offset_y=6, color="#2563EB30")

        hl = QHBoxLayout(hero)
        hl.setContentsMargins(32, 0, 32, 0)

        now = datetime.now()
        h = now.hour
        greeting = "Bonjour" if h < 12 else ("Bon après-midi" if h < 18 else "Bonsoir")
        date_fr  = f"{JOURS[now.weekday()]} {now.day} {MOIS[now.month-1]} {now.year}"

        left = QVBoxLayout(); left.setSpacing(4)
        g_lbl = QLabel(f"{greeting} 👋")
        g_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: white;")
        d_lbl = QLabel(date_fr)
        d_lbl.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.7);")
        left.addWidget(g_lbl); left.addWidget(d_lbl)
        hl.addLayout(left, 1)

        badge = QFrame()
        badge.setStyleSheet("background: rgba(255,255,255,0.15); border-radius: 12px;")
        badge.setFixedSize(120, 56)
        bl = QVBoxLayout(badge); bl.setContentsMargins(12,0,12,0); bl.setSpacing(2)
        bl.setAlignment(Qt.AlignCenter)
        self._kpi_patients_hero = QLabel("—")
        self._kpi_patients_hero.setStyleSheet("font-size: 24px; font-weight: 800; color: white;")
        self._kpi_patients_hero.setAlignment(Qt.AlignCenter)
        plbl = QLabel("patients")
        plbl.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.7);")
        plbl.setAlignment(Qt.AlignCenter)
        bl.addWidget(self._kpi_patients_hero); bl.addWidget(plbl)
        hl.addWidget(badge)
        root.addWidget(hero)

        # ── KPIs ──
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(14)
        self._kpi_p = KpiCard("👥", "—",  "Patients",    "enregistrés",     "#2563EB", "#EFF6FF")
        self._kpi_s = KpiCard("⚡", "0",   "Séances",     "ce mois",         "#7C3AED", "#F5F3FF")
        self._kpi_a = KpiCard("🔔", "0",   "Alertes",     "seuils dépassés", "#DC2626", "#FEF2F2")
        self._kpi_d = KpiCard("📡", "0/2", "Dispositifs", "en ligne",        "#059669", "#F0FDF4")
        for k in [self._kpi_p, self._kpi_s, self._kpi_a, self._kpi_d]:
            kpi_row.addWidget(k, 1)
        root.addLayout(kpi_row)

        # ── Corps ──
        body = QHBoxLayout(); body.setSpacing(16)

        # Gauche : patients récents
        left_col = QVBoxLayout(); left_col.setSpacing(0)

        patients_card = QFrame()
        patients_card.setStyleSheet("QFrame { background: white; border-radius: 16px; border: 1.5px solid #F1F5F9; }")
        _shadow(patients_card, blur=20, offset_y=3, color="#0000000D")
        self._p_layout = QVBoxLayout(patients_card)
        self._p_layout.setContentsMargins(0, 0, 0, 12)
        self._p_layout.setSpacing(0)

        ph = QHBoxLayout(); ph.setContentsMargins(16, 16, 16, 8)
        ptitle = QLabel("Patients récents")
        ptitle.setStyleSheet("font-size: 14px; font-weight: 700; color: #111827;")
        self._see_all = QLabel("Voir tout →")
        self._see_all.setStyleSheet("font-size: 12px; color: #2563EB; font-weight: 600;")
        self._see_all.setCursor(Qt.PointingHandCursor)
        ph.addWidget(ptitle, 1); ph.addWidget(self._see_all)
        self._p_layout.addLayout(ph)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #F1F5F9; background: #F1F5F9; max-height:1px; border:none;")
        self._p_layout.addWidget(sep)

        self._patients_body = QVBoxLayout()
        self._patients_body.setSpacing(0)
        self._patients_body.setContentsMargins(0, 4, 0, 0)
        loading = QLabel("Chargement...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet("color: #9CA3AF; font-size: 12px; padding: 32px;")
        self._patients_body.addWidget(loading)
        self._p_layout.addLayout(self._patients_body)

        left_col.addWidget(patients_card)
        body.addLayout(left_col, 3)

        # Droite
        right_col = QVBoxLayout(); right_col.setSpacing(14)

        # Accès rapide
        qa_card = QFrame()
        qa_card.setStyleSheet("background: white; border-radius: 16px; border: 1.5px solid #F1F5F9;")
        _shadow(qa_card, blur=20, offset_y=3, color="#0000000D")
        qal = QVBoxLayout(qa_card); qal.setContentsMargins(0, 0, 0, 12); qal.setSpacing(6)

        qah = QLabel("Accès rapide")
        qah.setStyleSheet("font-size: 14px; font-weight: 700; color: #111827; padding: 16px 16px 8px 16px;")
        qal.addWidget(qah)
        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #F1F5F9; background: #F1F5F9; max-height:1px; border:none;")
        qal.addWidget(sep2)

        for icon, lbl, col in [("👤","Nouveau patient","#2563EB"),("⚡","Démarrer une séance","#7C3AED"),("📊","Voir les résultats","#059669")]:
            b = QuickBtn(icon, lbl, col)
            wrap = QHBoxLayout(); wrap.setContentsMargins(12, 3, 12, 3)
            wrap.addWidget(b)
            qal.addLayout(wrap)

        right_col.addWidget(qa_card)

        # Dispositifs
        dev_card = QFrame()
        dev_card.setStyleSheet("background: white; border-radius: 16px; border: 1.5px solid #F1F5F9;")
        _shadow(dev_card, blur=20, offset_y=3, color="#0000000D")
        devl = QVBoxLayout(dev_card); devl.setContentsMargins(0, 0, 0, 8); devl.setSpacing(0)

        devh = QLabel("Dispositifs EEG")
        devh.setStyleSheet("font-size: 14px; font-weight: 700; color: #111827; padding: 16px 16px 8px 16px;")
        devl.addWidget(devh)
        sep3 = QFrame(); sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color: #F1F5F9; background: #F1F5F9; max-height:1px; border:none;")
        devl.addWidget(sep3)
        devl.addWidget(DeviceItem("Casque OpenBCI #1", False))
        devl.addWidget(DeviceItem("Casque OpenBCI #2", False))

        right_col.addWidget(dev_card)
        right_col.addStretch()
        body.addLayout(right_col, 2)
        root.addLayout(body, 1)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_patients()

    def _load_patients(self):
        req = QNetworkRequest(QUrl(f"{API_BASE}/patients?limit=200"))
        token = session.get_token()
        if token:
            req.setRawHeader(b"Authorization", f"Bearer {token}".encode())
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_patients(reply))

    def _on_patients(self, reply: QNetworkReply):
        if reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) != 200:
            return
        patients = json.loads(reply.readAll().data())
        count = len(patients)

        self._kpi_patients_hero.setText(str(count))
        self._kpi_p.val_lbl.setText(str(count))

        # Vider le body
        while self._patients_body.count():
            item = self._patients_body.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        recent = patients[-6:][::-1]
        if not recent:
            empty = QLabel("Aucun patient enregistré")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #9CA3AF; font-size: 12px; padding: 32px;")
            self._patients_body.addWidget(empty)
        else:
            for i, p in enumerate(recent):
                if i > 0:
                    self._patients_body.addWidget(_hdivider())
                self._patients_body.addWidget(PatientItem(p, i))
