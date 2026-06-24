# Changelog

Toutes les modifications notables du projet NeuralES sont documentées ici.  
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).  
Versionnement sémantique : [SemVer](https://semver.org/lang/fr/).

---

## [Unreleased] — develop

### Added
- Pipeline CI GitHub Actions : lint Python (ruff), type-check TypeScript, build production frontend
- Workflow de release automatique sur push de tag `v*.*.*`
- Templates de PR et d'issues (bug report, feature request, user story)
- CODEOWNERS et CONTRIBUTING.md
- Isolation organisationnelle complète sur tous les endpoints protégés
- Persistance des sessions d'acquisition en base (`t_session_mesure`)
- `list_by_organisation()` sur `SessionRepository`

### Fixed
- `current_user.organisation_id` → `current_user["organisation_id"]` dans analytics
- Filtre `deleted_at` manquant sur `SessionModel` supprimé
- Double bloc de nettoyage dans `backend/run.ps1`
- Clés env frontend `VITE_API_URL` → `VITE_API_BASE_URL` dans `setup.ps1`
- Cycle de vie du processus plink dans `run_with_plink.ps1`

### Removed
- Fichiers morts : `eeg_sleepedf.py`, `schemas/eeg.py`, fichier EDF sample
- Assets GLB non utilisés, composants Vue scaffold (HelloWorld, HelmetViewer3D)
- Dossier `temp/` et `mobile/` vides

---

## [1.0.0-alpha] — 2026-06-15

### Bloc 4 — Échanges de données (100%)
- **REST API** : 8 routers FastAPI (`auth`, `organisations`, `patients`, `devices`, `results`, `acquisition`, `analytics`, `eeg`)
- **WebSocket EEG** : streaming temps réel 50ms, ring buffer 10s, broadcast `fatigue_score` + `quality_score`
- **Tunnel SSH** : plink (PuTTY) → PostgreSQL VPS OVH via port local 5433
- **OpenAPI** : Swagger UI (`/docs`) + ReDoc (`/redoc`) auto-générés

### Bloc 3 — Développement (81%)
- **Clean Architecture** : 4 couches `api/` → `application/use_cases/` → `domain/` → `data/repositories/`
- **Traitement EEG** : `bandpower_fft()` FFT NumPy avec fenêtre Hanning, ratio θ/α → score fatigue 0-100, lecture EDF via MNE
- **Frontend Vue 3** : Pinia stores, TypeScript strict, Tailwind CSS 4, composants `Brain3D` (Three.js) + `EEGChartCanvas` (uPlot)
- **Desktop Tauri 2** : wrapper Rust cross-platform avec détection runtime `isDesktopRuntime()`, données offline mock SQLite
- **Desktop PyQt** : client Python/Qt avec pages acquisition, dashboard, patients, login

### Bloc 1 — Sécurité (65%)
- **Authentification JWT** : access token 2h + refresh token 7d HttpOnly cookie, PBKDF2-SHA256 260k itérations, `hmac.compare_digest`
- **Rotation JTI** : révocation des tokens en base à chaque refresh
- **RGPD** : `t_consentement` (scope, status, withdrawn_at), soft delete patients (`deleted_at`)
- **RBAC** : tables `t_role` / `t_permission` / `t_associer`
- **Schéma PostgreSQL** : 15+ tables préfixées `t_` avec organisation multi-tenant

### Infrastructure
- Monorepo : `backend/` (FastAPI) + `neurales-web/` (Vue 3 + Tauri) + `desktop/` (PyQt)
- Scripts PowerShell : `setup.ps1`, `backend/run.ps1`, `backend/run_with_plink.ps1`, `neurales-web/run.ps1`
- Convention de code : `docs/convention.md`

---

[Unreleased]: https://github.com/DylanNeural/NeuralES/compare/v1.0.0-alpha...HEAD
[1.0.0-alpha]: https://github.com/DylanNeural/NeuralES/releases/tag/v1.0.0-alpha
