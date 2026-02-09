# Backend - NeuralES

## Architecture

```
app/
├── api/                    ← API FastAPI (routes/schemas)
│   ├── routes/
│   │   ├── organisations.py
│   │   ├── eeg.py
│   │   └── health.py
│   ├── schemas/            ← Schémas Pydantic (validation API)
│   └── __init__.py
│
├── application/            ← Logique métier (use cases)
│   ├── use_cases/
│   ├── dtos/
│   ├── ports/              ← Interfaces (abstraction)
│   └── exceptions/
│
├── domain/                 ← Entités (cœur metier)
│   ├── entities/
│   └── exceptions/
│
├── data/                   ← Persistance (implémentation)
│   ├── repositories/
│   ├── models/
│   ├── db.py
│   └── sleep_edf/
│
├── core/                   ← Services transversaux
│   └── eeg_processor.py
│
├── config/                 ← Configuration
│   └── settings.py
│
└── main.py                 ← Point d'entrée FastAPI
```

## Installation

```bash
# 1. Créer venv
python -m venv venv
venv\Scripts\activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

## Démarrage

```bash
# Dev avec reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## API Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/health` | Health check |
| POST | `/organisations` | Créer une organisation |
| GET | `/organisations` | Lister les organisations |
| GET | `/organisations/{id}` | Récupérer une organisation |
| PATCH | `/organisations/{id}` | Mettre à jour |
| DELETE | `/organisations/{id}` | Supprimer |
| WS | `/eeg/stream` | WebSocket streaming EEG |

## WebSocket EEG

```python
import asyncio
import websockets

async def test_eeg():
    async with websockets.connect("ws://localhost:8000/eeg/stream") as ws:
        while True:
            msg = await ws.recv()
            print(msg)  # JSON avec fatigue, samples, etc.

asyncio.run(test_eeg())
```

## Structure Héxagonale

- **API** → Seul point d'entrée
- **Application** → Logique métier (use cases, DTOs)
- **Domain** → Entités (zéro dépendances externes)
- **Data** → Implémentations repositories
- **Core** → Services (traitement EEG, etc.)
