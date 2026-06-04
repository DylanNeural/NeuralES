# NeuralES — Contenu Diaporama Google Slides
## Ynov Campus Toulouse · Dylan Andrade Pereira · Juin 2026

---

## SLIDE 1 — Titre

**NeuralES**
*Système d'analyse EEG de la fatigue cognitive en temps réel*

Dylan Andrade Pereira
Ynov Campus Toulouse — Juin 2026

*[fond sombre, logo Ynov en bas à droite]*

---

## SLIDE 2 — Sommaire

1. Contexte & Problématique
2. Objectifs du projet
3. Architecture globale
4. Réalisations techniques
5. Démonstration
6. Difficultés rencontrées
7. Perspectives

---

## SLIDE 3 — Contexte : La fatigue cognitive, un enjeu invisible

- La fatigue cognitive affecte **concentration, réactivité et prise de décision**
- Difficile à mesurer objectivement (auto-déclaration peu fiable)
- Secteurs concernés : médecine, transport, industrie, sport de haut niveau

> *"Un pilote, un chirurgien ou un opérateur industriel fatigué représente un risque réel — mais invisible."*

*[illustration : courbe EEG ou image d'électrodes]*

---

## SLIDE 4 — L'EEG comme solution

- L'**électroencéphalogramme (EEG)** mesure l'activité électrique cérébrale
- Des patterns identifiables témoignent de la fatigue : augmentation des ondes **Thêta (4-8 Hz)**, diminution des ondes **Alpha (8-13 Hz)**
- Accessible grâce à des casques comme **OpenBCI** (~300€)

**Opportunité** : créer un outil desktop temps réel pour le suivi clinique

---

## SLIDE 5 — Problématique

> Comment concevoir une application desktop capable d'**acquérir, visualiser et analyser des signaux EEG en temps réel**, adaptée à un usage clinique ?

Contraintes :
- Traitement signal bas-latence
- Interface lisible par un professionnel de santé
- Architecture extensible (multi-patients, historique)

---

## SLIDE 6 — Objectifs du projet

| Objectif | Statut |
|---|---|
| Application desktop PySide6 complète | ✅ |
| Gestion des patients (CRUD) | ✅ |
| Acquisition EEG temps réel (WebSocket) | ✅ |
| Visualisation signal en temps réel | ✅ |
| Visualisation 3D (waterfall chart) | ✅ |
| Casque EEG 3D interactif | ✅ |
| Backend FastAPI + BDD PostgreSQL | ✅ |
| Connexion matériel OpenBCI | 🔄 En cours |

---

## SLIDE 7 — Architecture Globale

```
┌─────────────────────────────────────────────────────┐
│              APPLICATION DESKTOP (PySide6)           │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Patients  │  │  Acquisition │  │  Brain View │  │
│  │  (CRUD)    │  │  + Signaux   │  │  (Three.js) │  │
│  └────────────┘  └──────────────┘  └─────────────┘  │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP REST + WebSocket
┌───────────────────────▼─────────────────────────────┐
│              BACKEND FastAPI (Python)                 │
│         Sessions · Patients · EEG Stream             │
└───────────────────────┬─────────────────────────────┘
                        │ SSH Tunnel
┌───────────────────────▼─────────────────────────────┐
│         PostgreSQL (VPS OVH — Debian)                │
└─────────────────────────────────────────────────────┘
```

---

## SLIDE 8 — Stack Technique

**Backend**
- Python 3.11 · FastAPI · Uvicorn
- PostgreSQL 15 · SQLAlchemy · Alembic
- WebSocket (streaming EEG temps réel)

**Desktop**
- PySide6 (Qt 6) · pyqtgraph
- QWebEngineView · QWebChannel (bridge Python ↔ JS)
- Three.js (rendu 3D dans Qt)

**Infrastructure**
- VPS OVH (Debian) — PostgreSQL distant
- Tunnel SSH local (`localhost:5433 → VPS:5432`)

---

## SLIDE 9 — Application Desktop : Vue d'ensemble

*[screenshot de l'interface principale]*

Trois sections principales :
- **Patients** : liste filtrée, création de dossiers
- **Acquisition** : connexion EEG, visualisation temps réel
- **Vue casque** : sélection d'électrodes en 3D

Navigation latérale, thème sombre clinique.

---

## SLIDE 10 — Gestion des Patients

*[screenshot de la liste patients + formulaire création]*

**Liste patients**
- Avatars colorés, badges service, filtres dynamiques
- Recherche par nom, service, médecin

**Création de dossier**
- Informations personnelles (NSS, date de naissance, sexe)
- Informations médicales (service, médecin référent, notes)

---

## SLIDE 11 — Acquisition EEG : Architecture temps réel

```
Casque OpenBCI
      │
      ▼
Backend FastAPI
  POST /acquisition/start  →  session_id
  WS  /eeg/stream?session_id=XXX
      │
      ▼  (WebSocket, JSON chunks)
Application Desktop
  _on_ws_msg() → parse chunk → mise à jour graphique
```

Chaque chunk WebSocket contient :
- Liste des canaux EEG actifs
- Tableau d'échantillons (float, en Volts)
- Timestamp `t0` et fréquence d'échantillonnage `sfreq`

---

## SLIDE 12 — Visualisation Signal (Waveform classique)

*[screenshot du graphique pyqtgraph]*

- Bibliothèque **pyqtgraph** (rendu OpenGL désactivé pour compatibilité D3D11)
- Défilement temps réel, buffer circulaire
- Couleur par canal, axe temps relatif

---

## SLIDE 13 — Visualisation 3D (Three.js Waterfall Chart)

*[screenshot du graphique 3D]*

- Rendu **Three.js** intégré dans Qt via **QWebEngineView**
- Chaque canal EEG = une ligne 3D empilée en Z
- Défilement temporel sur l'axe X (fenêtre glissante 10s)
- **Auto-scaling** au premier chunk : `ampScale = 55 / maxAbsValue`
- Brouillard exponentiel, grille de fond, contrôles orbitaux

---

## SLIDE 14 — Casque EEG 3D Interactif

*[screenshot du casque 3D avec électrodes]*

- Modèle **GLB** chargé via `GLTFLoader` (Three.js)
- Électrodes nommées (`Electrode_Fp1`, `Electrode_Cz`, etc.)
- **Clic sur électrode** → sélection envoyée à Python via `QWebChannel`
- Coloration par score de fatigue (rouge = activité élevée)

Communication bidirectionnelle :
- Python → JS : `setElectrodeScore(name, score)`
- JS → Python : `bridge.on_electrode_click(json)`

---

## SLIDE 15 — Bridge Python ↔ JavaScript (QWebChannel)

*[schéma technique]*

```python
# Python (PySide6)
class Bridge(QObject):
    @Slot(str)
    def on_electrode_click(self, data):
        info = json.loads(data)
        # Traitement côté Python
```

```javascript
// JavaScript (Three.js)
new QWebChannel(qt.webChannelTransport, ch => {
    window._bridge = ch.objects.bridge;
});
// Envoyer vers Python :
window._bridge.on_electrode_click(JSON.stringify({electrode, active}));
```

→ Communication **synchrone, sans serveur intermédiaire**

---

## SLIDE 16 — Serveur HTTP local embarqué

Problème : QWebEngineView ne peut pas charger des fichiers locaux avec import ES modules (Three.js).

Solution : **serveur HTTP Python embarqué** (port aléatoire au démarrage)

```python
httpd = socketserver.TCPServer(('127.0.0.1', 0), Handler)
# Sert : /vendor/three.module.js, /vendor/OrbitControls.js, etc.
```

Import map dans le HTML :
```json
{ "three": "/vendor/three.module.js",
  "three/addons/": "/vendor/" }
```

---

## SLIDE 17 — Difficultés Techniques

| Problème | Solution |
|---|---|
| Conflit D3D11 / OpenGL (Qt + pyqtgraph) | `pg.setConfigOptions(useOpenGL=False)` |
| CDN Three.js inaccessible dans Qt WebEngine | Vendor local + serveur HTTP embarqué |
| Échelle EEG : valeurs en Volts (±0.0001) | Auto-scaling dynamique au 1er chunk |
| QTextEdit vole les scroll events | `wheelEvent = lambda e: e.ignore()` |
| Backend se ferme immédiatement | Double bloc `finally` en PowerShell → supprimé |
| VPS PostgreSQL injoignable | Redémarrage depuis panel OVH |

---

## SLIDE 18 — Démonstration

*[section live demo]*

Scénario :
1. Lancement backend (FastAPI + tunnel SSH)
2. Ouverture application desktop
3. Création d'un patient
4. Lancement session d'acquisition
5. Visualisation signal temps réel (waveform)
6. Bascule vers graphique 3D waterfall
7. Vue casque EEG — sélection d'électrodes

---

## SLIDE 19 — Résultats

- Application **fonctionnelle de bout en bout** sur Windows 11
- Latence WebSocket → rendu graphique : **< 100ms**
- Support de **multiples canaux EEG** simultanés
- Interface utilisable par un non-technicien
- Base de données persistante sur infrastructure cloud

---

## SLIDE 20 — Perspectives

**Court terme**
- Connexion réelle au matériel **OpenBCI** (BrainFlow SDK)
- Algorithme de détection de fatigue (bandes fréquentielles Thêta/Alpha)
- Export de sessions en CSV / EDF

**Moyen terme**
- Application mobile (React Native / Tauri)
- Dashboard web Vue 3 pour les médecins
- Alertes en temps réel (seuils configurables)

**Long terme**
- Modèle ML de classification de fatigue
- Conformité dispositif médical (CE, FDA)

---

## SLIDE 21 — Conclusion

- NeuralES démontre la **faisabilité technique** d'un outil EEG desktop moderne
- Stack Python/Qt performante pour du traitement signal temps réel
- Architecture **modulaire et extensible** : backend, desktop, web, mobile
- Base solide pour intégrer un algorithme de détection de fatigue réel

> *"Du signal brut à la décision clinique — une brique à la fois."*

---

## SLIDE 22 — Questions ?

**NeuralES**
Dylan Andrade Pereira — Ynov Campus Toulouse

*Merci pour votre attention*

[GitHub / démo disponible sur demande]
