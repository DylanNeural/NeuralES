# NeuralES
Analyse des signaux EEG pour estimer la fatigue avec un casque a electrodes.

## Structure

- backend/ : API FastAPI + traitement EEG.
- neurales-web/ : application web Vue 3 + Vite.
- desktop/ : application desktop Python.

## Demarrage rapide (Windows)

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Option script : `backend/run.ps1` ou `backend/run.bat` (venv requis, PostgreSQL dans le PATH).

### Web

```powershell
cd neurales-web
npm install
npm run dev
```

Option script : `neurales-web/run.ps1` ou `neurales-web/run.bat` (cree .env et installe les deps si besoin).

### Desktop

```powershell
cd desktop
.\run.ps1
```

Le script desktop cree le venv et installe les dependances si necessaire.

## Documentation

- Architecture backend : [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md)
- Auth : [docs/authentication.md](docs/authentication.md)
- Conventions : [docs/convention.md](docs/convention.md)
