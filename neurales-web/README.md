# NeuralES Web

Application web Vue 3 + Vite pour l'interface NeuralES.

## Prerequis

- Node.js 18+
- npm

## Lancer en dev

```powershell
npm install
npm run dev
```

Le serveur tourne par defaut sur http://localhost:5173.

## Script Windows

`run.ps1` (ou `run.bat`) :
- cree un `.env` si besoin
- installe les dependances
- demarre Vite

## Build

```powershell
npm run build
npm run preview
```

## Assets publics

Les fichiers statiques (GLB, SVG, JSON) sont dans [public/](public/).
