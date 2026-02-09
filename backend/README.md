# NeuralES Backend

API REST FastAPI pour NeuralES - Système de lecture et d'analyse EEG en temps réel.

## 🏗️ Architecture Hexagonale

```
app/
├── api/                           ← Interface utilisateur
│   ├── routes/                    ← Endpoints FastAPI
│   │   ├── organisations.py       └─ CRUD organisations
│   │   ├── eeg.py                 └─ WebSocket streaming EEG
│   │   └── health.py              └─ Healthcheck
│   └── schemas/                   ← Schémas Pydantic (validation)
│       ├── organisation.py
│       └── eeg.py
│
├── application/                   ← Logique métier
│   ├── use_cases/                 ← Actions métier
│   │   ├── create_organisation.py
│   │   ├── get_organisation.py
│   │   ├── list_organisations.py
│   │   ├── update_organisation.py
│   │   └── delete_organisation.py
│   ├── dtos/                      ← Data Transfer Objects internes
│   ├── ports/                     ← Interfaces (abstraction)
│   │   └── organisation_repository.py
│   └── exceptions/                └─ Exceptions custom
│
├── domain/                        ← Cœur métier (INDÉPENDANT)
│   ├── entities/
│   │   └── organisation.py
│   └── exceptions/
│
├── data/                          ← Couche données
│   ├── repositories/              ← Implémentations des ports
│   │   └── organisation_repository.py
│   ├── models/                    └─ ORM SQLAlchemy
│   └── db.py                      └─ Configuration BD
│
├── core/                          ← Services techniques
│   └── eeg_processor.py           └─ Traitement EEG (DSP, FFT)
│
├── config/                        ← Configuration
│   └── settings.py                └─ Variables d'env centralisées
│
└── main.py                        ← Point d'entrée FastAPI
```

## 📋 Prérequis

- Python 3.9+
- PostgreSQL 12+
- pip

## 🚀 Installation Rapide

### Option 1: Script automatique (Windows)

```powershell
# PowerShell
.\setup.ps1

# CMD
setup.bat
```

### Option 2: Installation manuelle

```bash
# 1. Créer environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Copier et configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres

# 4. Vérifier les imports
python check_imports.py

# 5. Lancer le serveur
python -m uvicorn app.main:app --reload
```

## 📡 Endpoints API

### Health Check
```http
GET /health
```

### Organisations (CRUD)
```http
POST   /organisations                # Créer
GET    /organisations                # Lister
GET    /organisations/{id}           # Récupérer
PATCH  /organisations/{id}           # Mettre à jour
DELETE /organisations/{id}           # Supprimer
```

**Exemple POST:**
```json
{
  "nom": "Hôpital ABC",
  "type": "hospital",
  "adresse": "123 Rue de la Paix"
}
```

### EEG WebSocket
```
WS /eeg/stream
```

**Message reçu (chaque 50ms):**
```json
{
  "t0": 0.0,
  "sfreq": 100.0,
  "channels": ["Fpz-Cz", "Pz-Oz"],
  "samples": [[...], [...]],
  "fatigue": 42,
  "quality": "Good",
  "alerts": [],
  "chunk_seconds": 0.05,
  "window_seconds": 10.0
}
```

**Client Python:**
```python
import asyncio
import websockets
import json

async def stream_eeg():
    async with websockets.connect("ws://localhost:8000/eeg/stream") as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"Fatigue: {data['fatigue']}")

asyncio.run(stream_eeg())
```

## 🔧 Configuration

Créer un fichier `.env` :

```env
# Environnement
DEBUG=False

# Base de données
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/neurales

# EEG
CHUNK_SECONDS=0.05
FATIGUE_WINDOW_SECONDS=10.0
THETA_MIN=4.0
THETA_MAX=8.0
ALPHA_MIN=8.0
ALPHA_MAX=12.0
FATIGUE_RATIO_MIN=0.5
FATIGUE_RATIO_MAX=3.0
```

## 📚 Documentation

- **Interactive API Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc
- **Architecture Details:** [ARCHITECTURE.md](ARCHITECTURE.md)

## ⚡ Scripts Utiles

```bash
# Vérifier les imports
python check_imports.py

# Lancer tests (quand implémentés)
pytest tests/

# Format code
black app/

# Linting
flake8 app/
```

## 🧠 Algorithme Fatigue EEG

Score fatigue basé sur le **ratio theta/alpha** :

```
1. FFT sur fenêtre glissante 10s
2. Extraire puissance bande theta (4-8 Hz)
3. Extraire puissance bande alpha (8-12 Hz)
4. Calculer ratio = theta / alpha
5. Normaliser vers 0-100
```

**Interprétation :**
- 0-30 : Alerte (repos)
- 30-70 : Normal
- 70-100 : Fatigue détectée

## 🐛 Dépannage

### Erreur: `postgresql: command not found`
→ PostgreSQL n'est pas dans le PATH. Installer ou ajouter au PATH.

### Erreur: `pydantic_settings` not found
→ Réinstaller: `pip install pydantic-settings`

### WebSocket timeout
→ Vérifier que le fichier `SC4001E0-PSG.edf` existe dans `app/data/sleep_edf/`

## 📝 Stack Technique

| Composant | Version | Usage |
|-----------|---------|-------|
| FastAPI | 0.115.6 | Framework web |
| Uvicorn | 0.32.1 | Serveur ASGI |
| SQLAlchemy | 2.0.23 | ORM |
| Pydantic | 2.x | Validation |
| MNE | Latest | Traitement EEG |
| NumPy | Latest | Calculs numériques |

## 📄 Licence

[Voir LICENSE](../LICENSE)

## 👥 Contributeurs

- Dylan (Architecture hexagonale refactoring)

---

**Dernière mise à jour:** Février 2026
