# Rapport Technique — NeuralES
## Système d'analyse EEG de la fatigue cognitive en temps réel

---

**Auteur** : Dylan Andrade Pereira  
**Établissement** : Ynov Campus Toulouse  
**Date** : Juin 2026  
**Projet** : Fil rouge — Application desktop EEG  

---

## Table des matières

1. Introduction
2. Contexte et problématique
3. Analyse des besoins
4. Architecture du système
5. Réalisations techniques
   - 5.1 Backend FastAPI
   - 5.2 Application desktop PySide6
   - 5.3 Visualisation des signaux
   - 5.4 Intégration Three.js dans Qt
6. Difficultés rencontrées et solutions
7. Tests et validation
8. Perspectives d'évolution
9. Conclusion
10. Annexes

---

## 1. Introduction

NeuralES est une application desktop de surveillance et d'analyse de signaux EEG (électroencéphalogramme) développée dans le cadre du projet fil rouge à Ynov Campus Toulouse. L'objectif est de fournir aux professionnels de santé un outil permettant d'acquérir, visualiser et analyser en temps réel l'activité cérébrale de patients, avec une attention particulière à la détection de la fatigue cognitive.

Le projet couvre l'ensemble de la chaîne technique : de l'acquisition du signal brut via un casque EEG jusqu'à sa représentation visuelle dans une interface graphique moderne.

---

## 2. Contexte et Problématique

### 2.1 La fatigue cognitive

La fatigue cognitive est un état de dégradation des performances mentales résultant d'une activité intellectuelle soutenue. Elle se manifeste par une diminution de la concentration, une augmentation du temps de réaction et une altération de la prise de décision. Contrairement à la fatigue physique, elle est difficile à détecter de manière objective par observation directe.

Dans des domaines à haute responsabilité tels que la médecine, l'aviation ou l'industrie, la fatigue cognitive représente un risque sérieux pour la sécurité. Les méthodes actuelles de détection reposent principalement sur des questionnaires subjectifs (échelle de Karolinska, test de Stroop), insuffisants pour un suivi en temps réel.

### 2.2 L'EEG comme outil de mesure

L'électroencéphalogramme mesure l'activité électrique du cerveau via des électrodes posées sur le scalp. Les signaux obtenus sont caractérisés par des bandes fréquentielles spécifiques :

| Bande | Fréquence | Lien avec la fatigue |
|---|---|---|
| Delta | 0.5–4 Hz | Sommeil profond |
| Thêta | 4–8 Hz | Somnolence, augmente avec la fatigue |
| Alpha | 8–13 Hz | Relaxation, diminue avec la vigilance |
| Bêta | 13–30 Hz | Concentration active |
| Gamma | > 30 Hz | Traitement cognitif intense |

Des études montrent qu'une augmentation du ratio Thêta/Alpha est un marqueur fiable de la fatigue cognitive. C'est sur cette base que NeuralES vise à construire son algorithme de détection.

### 2.3 Matériel ciblé : OpenBCI

OpenBCI est un fabricant américain de casques EEG open-source à destination de la recherche. Le modèle Ultracortex Mark IV, utilisé comme cible pour ce projet, propose 8 à 16 canaux EEG avec une fréquence d'échantillonnage de 250 Hz. Son SDK BrainFlow (Python) permet une intégration simple dans des applications tierces.

### 2.4 Problématique

Comment concevoir une application desktop capable d'acquérir des signaux EEG en temps réel depuis un casque OpenBCI, de les transmettre via une API, et de les visualiser de manière exploitable par un professionnel de santé, tout en maintenant une architecture extensible permettant d'intégrer un algorithme de détection de fatigue ?

---

## 3. Analyse des Besoins

### 3.1 Besoins fonctionnels

**Gestion des patients**
- Créer un dossier patient (informations personnelles et médicales)
- Lister les patients avec filtres (service, médecin, nom)
- Accéder au dossier d'un patient

**Acquisition EEG**
- Démarrer et arrêter une session d'acquisition
- Recevoir les données EEG en temps réel
- Associer une session à un patient

**Visualisation**
- Afficher les signaux EEG en temps réel (forme d'onde)
- Proposer une vue alternative en graphique 3D
- Visualiser les électrodes actives sur un modèle de casque 3D
- Sélectionner des électrodes individuellement

**Persistance**
- Sauvegarder les sessions et les données patients en base de données

### 3.2 Besoins non fonctionnels

- Interface utilisable sur Windows 11
- Latence de rendu < 200ms après réception d'un chunk WebSocket
- Thème sombre adapté à un usage clinique prolongé
- Architecture découplée backend/frontend

### 3.3 Périmètre du projet fil rouge

Pour ce premier semestre, le périmètre se concentre sur la pile technique complète (backend + desktop) avec des données EEG provenant d'un fichier de test (Sleep EDF, PhysioNet). La connexion au matériel OpenBCI réel sera implémentée en phase 2.

---

## 4. Architecture du Système

### 4.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION DESKTOP                         │
│                     (PySide6 / Qt 6)                        │
│  ┌─────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │   Patients  │  │   Acquisition   │  │   Brain View   │  │
│  │  (PySide6)  │  │   (pyqtgraph    │  │  (Three.js /   │  │
│  │             │  │   + Three.js)   │  │  QWebEngine)   │  │
│  └─────────────┘  └────────┬────────┘  └────────────────┘  │
└───────────────────────────┬┴────────────────────────────────┘
                             │
                    HTTP REST + WebSocket
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      BACKEND                                  │
│                  FastAPI + Uvicorn                            │
│   ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│   │  /patients   │  │  /acquisition │  │   /eeg/stream  │  │
│   │   (CRUD)     │  │  start/stop   │  │   (WebSocket)  │  │
│   └──────────────┘  └───────────────┘  └────────────────┘  │
│                            │                                  │
│                     SQLAlchemy ORM                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                         SSH Tunnel
                      (localhost:5433)
                             │
┌────────────────────────────▼────────────────────────────────┐
│              PostgreSQL 15 (VPS OVH — Debian)                │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Choix technologiques

**PySide6** a été retenu pour l'application desktop pour plusieurs raisons :
- Intégration native avec l'écosystème Python (NumPy, MNE, BrainFlow)
- QWebEngineView permet d'embarquer du rendu WebGL (Three.js)
- Portabilité Windows/Linux/macOS
- Interface de qualité native (pas d'Electron)

**FastAPI** a été choisi pour le backend pour sa performance asynchrone native (asyncio), sa génération automatique de documentation (Swagger/ReDoc) et son support natif des WebSockets.

**PostgreSQL** sur VPS OVH permet de centraliser les données patients et les sessions EEG sur une infrastructure partagée accessible depuis plusieurs postes.

### 4.3 Communication inter-composants

| Lien | Protocole | Usage |
|---|---|---|
| Desktop → Backend | HTTP REST | CRUD patients, start/stop sessions |
| Desktop → Backend | WebSocket | Réception données EEG temps réel |
| Backend → PostgreSQL | TCP (SSH tunnel) | Requêtes SQL via SQLAlchemy |
| Python → JavaScript | QWebChannel | Contrôle Three.js depuis Python |
| JavaScript → Python | QWebChannel (Signal/Slot) | Retour clics électrodes |

---

## 5. Réalisations Techniques

### 5.1 Backend FastAPI

Le backend est structuré en modules distincts :

```
backend/app/
├── main.py           # Entrée uvicorn, CORS, routers
├── database.py       # Connexion SQLAlchemy, session
├── models.py         # Modèles ORM (Patient, Session, EEGData)
├── routers/
│   ├── patients.py   # GET/POST/PUT/DELETE /patients
│   └── acquisition.py# POST /acquisition/start|stop, WS /eeg/stream
└── schemas.py        # Schémas Pydantic (validation I/O)
```

**Endpoint WebSocket `/eeg/stream`**

Le backend lit un fichier EDF (format européen standard pour l'EEG) via la bibliothèque `mne`, puis envoie des chunks JSON à 10 Hz :

```python
@router.websocket("/eeg/stream")
async def eeg_stream(websocket: WebSocket, session_id: str):
    await websocket.accept()
    raw = mne.io.read_raw_edf(EDF_PATH, preload=True)
    sfreq = raw.info['sfreq']
    chunk_size = int(sfreq * 0.1)  # 100ms de données
    
    for start in range(0, raw.n_times, chunk_size):
        data, times = raw[:, start:start+chunk_size]
        payload = {
            "channels": raw.ch_names,
            "samples": data.tolist(),
            "t0": float(times[0]),
            "sfreq": sfreq
        }
        await websocket.send_json(payload)
        await asyncio.sleep(0.1)
```

### 5.2 Application Desktop PySide6

L'application est organisée en pages autonomes dans un `QStackedWidget` :

```
desktop/app/
├── main.py              # QApplication, MainWindow, navigation
├── pages/
│   ├── patients_list.py # Liste patients (filtres, avatars, badges)
│   ├── patient_create.py# Formulaire création patient
│   └── acquisition.py   # Acquisition EEG + visualisation
└── ui/
    ├── brain_view.py    # QWebEngineView casque 3D
    └── chart3d_view.py  # QWebEngineView graphique 3D
```

**Navigation** : une barre latérale avec `QPushButton` bascule entre les pages via `QStackedWidget.setCurrentIndex()`.

**Gestion des patients**

La page `patients_list.py` implémente :
- Un composant `AvatarLabel` : cercle coloré avec initiales, couleur dérivée du hash du nom
- Un `BadgeLabel` : pastille de couleur pour le service médical
- Quatre KPI cards (stats) en en-tête
- Filtrage en temps réel par nom (QLineEdit), service et médecin (QComboBox)
- Tableau `QTableWidget` avec widgets personnalisés par cellule

**Formulaire création de patient**

`patient_create.py` résout un problème courant avec PySide6 : les formulaires longs qui ne scrollent pas correctement. La solution retenue est une architecture explicite `QScrollArea` → `QWidget (content)` → layout vertical avec tous les champs, sans footer fixe.

```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)
content = QWidget()
layout = QVBoxLayout(content)
# ... tous les champs ...
# Boutons à la fin du layout (pas de footer fixe)
scroll.setWidget(content)
```

**Page d'acquisition**

Cette page gère :
1. La connexion HTTP au backend pour créer une session (`QNetworkAccessManager`)
2. La connexion WebSocket pour recevoir les données (`QWebSocket`)
3. Le buffer circulaire NumPy pour le rendu waveform
4. La transmission des données au graphique 3D

```python
def _start_session(self):
    req = QNetworkRequest(QUrl(f"{HTTP_BASE}/acquisition/start"))
    req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
    body = QByteArray(json.dumps({"patient_id": self._patient_id}).encode())
    reply = self._nam.post(req, body)
    reply.finished.connect(lambda: self._on_session_ready(reply))

def _on_session_ready(self, reply):
    data = json.loads(reply.readAll().data())
    session_id = data["session_id"]
    self._ws.open(QUrl(f"{WS_BASE}/eeg/stream?session_id={session_id}"))
```

### 5.3 Visualisation des signaux

**Waveform (pyqtgraph)**

Un `PlotWidget` pyqtgraph affiche les courbes EEG en défilement. Chaque canal dispose d'un buffer circulaire NumPy de 5000 points (≈20s à 250Hz). La mise à jour se fait à chaque chunk WebSocket via `setData()`.

Problème rencontré : conflit entre le backend D3D11 de Qt WebEngine et le renderer OpenGL de pyqtgraph, causant un crash au démarrage.

Solution : `pg.setConfigOptions(useOpenGL=False, antialias=False)` désactive le renderer OpenGL de pyqtgraph, laissant le D3D11 de Qt WebEngine opérer seul.

**Graphique 3D waterfall (Three.js)**

Un composant `Chart3DView` (`QWebEngineView`) charge `chart3d.html`, une scène Three.js avec un graphique waterfall 3D :
- Chaque canal EEG = une `THREE.Line` avec `BufferGeometry`
- Les canaux sont empilés selon l'axe Z (`Z_STEP = -90`)
- L'axe X représente le temps (fenêtre glissante de 10 secondes)
- L'axe Y représente l'amplitude du signal

Buffer circulaire côté JavaScript :
```javascript
buffers[name] = {
    xs: new Float32Array(MAX_PTS),  // timestamps
    ys: new Float32Array(MAX_PTS),  // amplitudes
    writeIdx: 0,
    count: 0
};
```

Auto-scaling dynamique : les signaux EEG bruts sont en Volts (±0.0001V). Sans mise à l'échelle, les courbes sont invisibles. Au premier chunk reçu, l'application calcule un facteur d'échelle :

```javascript
function computeScale(samples) {
    let maxAbs = 0;
    for (const ch of samples)
        for (const v of ch)
            if (Math.abs(v) > maxAbs) maxAbs = Math.abs(v);
    if (maxAbs > 0) ampScale = 55 / maxAbs;
}
```

### 5.4 Intégration Three.js dans Qt (QWebEngineView)

L'intégration de Three.js dans une application PySide6 nécessite plusieurs mécanismes :

**Serveur HTTP local embarqué**

Qt WebEngine n'autorise pas les modules ES6 sur des URLs `file://`. Un serveur HTTP Python est démarré au lancement de l'application sur un port aléatoire :

```python
class _MultiDirHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        for base in _BASES:
            path = base / self.path.lstrip('/')
            if path.is_file():
                # servir le fichier
                break

httpd = socketserver.TCPServer(('127.0.0.1', 0), _MultiDirHandler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
port = httpd.server_address[1]
```

Les ressources servies incluent :
- `/vendor/three.module.js` — Three.js r168
- `/vendor/OrbitControls.js` — contrôles caméra
- `/vendor/GLTFLoader.js` — chargement modèles 3D
- `/utils/BufferGeometryUtils.js` — dépendance GLTFLoader
- `/brain.html`, `/chart3d.html` — applications Three.js

**Import map** dans chaque HTML :
```html
<script type="importmap">
{
    "imports": {
        "three": "/vendor/three.module.js",
        "three/addons/": "/vendor/"
    }
}
</script>
```

**QWebChannel — communication bidirectionnelle**

QWebChannel est le mécanisme de communication entre Python et JavaScript dans Qt WebEngine.

Côté Python :
```python
class Bridge(QObject):
    @Slot(str)
    def on_electrode_click(self, json_str):
        data = json.loads(json_str)
        # Traitement de la sélection d'électrode

channel = QWebChannel()
channel.registerObject('bridge', self._bridge)
self.page().setWebChannel(channel)
```

Côté JavaScript :
```javascript
// qwebchannel.js doit être chargé en premier
new QWebChannel(qt.webChannelTransport, ch => {
    window._bridge = ch.objects.bridge;
});
// Appel vers Python :
window._bridge.on_electrode_click(JSON.stringify({electrode: 'Fp1', active: true}));
```

**Casque EEG 3D**

Le modèle `casque_brain_electrodes.glb` est un fichier GLB contenant :
- Un mesh `Casque` (le casque lui-même)
- Des meshes `Electrode_Fp1`, `Electrode_Cz`, etc. (une par électrode standard 10-20)

Lors du chargement, les meshes d'électrodes sont indexés et rendus interactifs (Raycaster Three.js pour la détection de clic).

---

## 6. Difficultés Rencontrées et Solutions

### 6.1 Conflit D3D11 / OpenGL

**Problème** : Qt WebEngine utilise D3D11 (DirectX 11) sur Windows comme backend graphique. pyqtgraph, en mode OpenGL, tente d'initialiser un contexte OpenGL dans la même fenêtre, ce qui provoque un crash.

**Solution** : désactiver OpenGL dans pyqtgraph avant tout import Qt :
```python
import pyqtgraph as pg
pg.setConfigOptions(useOpenGL=False, antialias=False)
```

### 6.2 Three.js inaccessible depuis Qt WebEngine

**Problème** : les CDN three.js (jsDelivr, unpkg) sont bloqués ou inaccessibles depuis Qt WebEngine. Les URLs `file://` ne supportent pas les imports ES6.

**Solution** : télécharger les fichiers vendor localement et les servir via un serveur HTTP Python embarqué avec import map.

### 6.3 Échelle des signaux EEG

**Problème** : les signaux EEG du fichier EDF sont en Volts (±0.0001V). Sans mise à l'échelle, les courbes Three.js ont une hauteur de 0.0001 unité — visuellement une ligne droite.

**Solution** : auto-scaling dynamique calculé sur le premier chunk reçu. Ce mécanisme est aussi robuste pour des signaux en µV (±100µV) — l'échelle s'adapte automatiquement.

### 6.4 Session WebSocket requise

**Problème** : l'endpoint `/eeg/stream` du backend requiert un `session_id` créé au préalable par `POST /acquisition/start`. Sans session active, la connexion WebSocket est refusée.

**Solution** : ajout d'un flux asynchrone HTTP → WebSocket :
1. `POST /acquisition/start` via `QNetworkAccessManager`
2. À la réception du `session_id`, ouverture du WebSocket
3. `POST /acquisition/stop` à l'arrêt

### 6.5 Scroll du formulaire patient cassé

**Problème** : le formulaire de création patient ne scrollait pas jusqu'en bas. Un `QTextEdit` (champ Remarques) interceptait les événements scroll de la molette.

**Solution** :
```python
self.f_remarques.wheelEvent = lambda e: e.ignore()
```

### 6.6 VPS PostgreSQL inaccessible

**Problème** : lors des premiers tests, le VPS OVH hébergeant PostgreSQL était hors ligne.

**Solution** : redémarrage depuis le panel d'administration OVH (Cloud → Serveurs → Redémarrer). Après redémarrage, le tunnel SSH et la connexion backend ont fonctionné normalement.

---

## 7. Tests et Validation

### 7.1 Tests manuels

Les fonctionnalités ont été validées par tests manuels sur Windows 11 :

| Fonctionnalité | Résultat |
|---|---|
| Lancement application | ✅ Fonctionnel |
| Création patient | ✅ Sauvegarde en BDD |
| Liste patients + filtres | ✅ Filtrage temps réel |
| Scroll formulaire | ✅ Jusqu'en bas |
| Connexion backend | ✅ HTTP + WebSocket |
| Réception données EEG | ✅ Chunks 100ms |
| Affichage waveform | ✅ Défilement temps réel |
| Graphique 3D | ✅ Waterfall animé |
| Casque 3D | ✅ Électrodes cliquables |
| Communication JS↔Python | ✅ QWebChannel opérationnel |

### 7.2 Données de test

Les données EEG utilisées proviennent du dataset **Sleep-EDF** (PhysioNet), un ensemble de données cliniques open-source d'enregistrements polysomnographiques. Le format EDF (European Data Format) est le standard international pour les données EEG cliniques.

---

## 8. Perspectives d'Évolution

### 8.1 Court terme

**Connexion OpenBCI réelle**  
Intégration de BrainFlow SDK pour remplacer la lecture EDF par un flux temps réel depuis un casque OpenBCI Ultracortex. BrainFlow expose une API Python unifiée pour de nombreux appareils EEG.

**Algorithme de détection de fatigue**  
Implémentation d'une analyse fréquentielle en temps réel :
1. FFT glissante sur fenêtre de 4 secondes
2. Calcul des puissances des bandes Thêta (4-8 Hz) et Alpha (8-13 Hz)
3. Indice de fatigue = Thêta / Alpha
4. Affichage d'une alerte si l'indice dépasse un seuil configurable

**Export de données**  
Export des sessions en CSV et EDF pour intégration avec des outils d'analyse externe (EEGLAB, MNE-Python).

### 8.2 Moyen terme

- **Application mobile** : React Native pour un accès aux sessions depuis smartphone
- **Dashboard web** : Vue 3 pour les médecins (historique des sessions, graphiques de tendance)
- **Authentification** : JWT tokens, gestion des rôles (médecin, technicien, admin)

### 8.3 Long terme

- **Modèle ML** : classification de la fatigue par réseau de neurones (LSTM ou Transformer sur séries temporelles EEG)
- **Conformité médicale** : démarches CE (Europe) pour usage en contexte clinique
- **Multi-patients simultanés** : suivi de plusieurs patients en parallèle (salle de réveil, service de soins)

---

## 9. Conclusion

NeuralES démontre la faisabilité technique d'un outil complet d'analyse EEG en temps réel sur desktop. En partant d'un signal brut issu d'un fichier EDF clinique, l'application est capable de l'acheminer depuis un backend FastAPI vers une interface PySide6, et de l'afficher à la fois sous forme de courbes classiques et de graphique 3D waterfall interactif.

Le projet a nécessité de résoudre plusieurs défis techniques non triviaux : intégration de Three.js (WebGL) dans une application Qt native, communication bidirectionnelle Python ↔ JavaScript via QWebChannel, et gestion de l'échelle des signaux biomédicaux.

L'architecture mise en place — backend FastAPI indépendant, desktop PySide6 modulaire, ressources 3D servies localement — offre une base solide pour l'implémentation de la prochaine étape : la connexion à un vrai casque OpenBCI et l'algorithme de détection de fatigue.

---

## 10. Annexes

### Annexe A — Structure du projet

```
NeuralES/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── patients.py
│   │   │   └── acquisition.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── run.ps1
│   └── requirements.txt
├── desktop/
│   ├── app/
│   │   ├── main.py
│   │   ├── pages/
│   │   │   ├── patients_list.py
│   │   │   ├── patient_create.py
│   │   │   └── acquisition.py
│   │   ├── ui/
│   │   │   ├── brain_view.py
│   │   │   └── chart3d_view.py
│   │   └── ressources/
│   │       ├── brain.html
│   │       ├── chart3d.html
│   │       ├── vendor/         (Three.js, OrbitControls, GLTFLoader)
│   │       └── utils/          (BufferGeometryUtils)
│   └── run.ps1
└── neurales-web/               (Vue 3 — frontend web)
```

### Annexe B — Dépendances

**Backend**
```
fastapi>=0.110
uvicorn[standard]
sqlalchemy>=2.0
psycopg2-binary
mne
python-multipart
websockets
```

**Desktop**
```
PySide6>=6.6
PySide6-WebEngine
pyqtgraph
numpy
```

### Annexe C — Format des données WebSocket

```json
{
  "channels": ["EEG Fpz-Cz", "EEG Pz-Oz"],
  "samples": [
    [-0.000045, 0.000023, 0.000067, ...],
    [0.000012, -0.000089, 0.000034, ...]
  ],
  "t0": 142.3,
  "sfreq": 100.0
}
```

- `channels` : liste des noms de canaux (norme 10-20)
- `samples` : tableau 2D [canal][échantillon], valeurs en Volts
- `t0` : timestamp du premier échantillon du chunk (secondes depuis début enregistrement)
- `sfreq` : fréquence d'échantillonnage en Hz

### Annexe D — Commandes de lancement

**Backend**
```powershell
cd backend
.\run.ps1
# Lance tunnel SSH + uvicorn sur :8000
```

**Desktop**
```powershell
cd desktop
.\run.ps1
# Lance python -m app.main
```
