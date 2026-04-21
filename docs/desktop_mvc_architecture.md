# Desktop MVC Architecture (Tauri)

## Objectif

Construire une application desktop autonome, sans backend distant, avec une architecture MVC claire et evolutive.

## Structure retenue

Dans `neurales-web/src-tauri/src` :

- `models/`: structures de donnees et DTOs (Model)
- `repositories/`: acces et persistance des donnees (Model persistence)
- `services/`: regles metier (Service layer)
- `controllers/`: commandes Tauri exposees au front (Controller)
- `app_state.rs`: wiring de l'application (injection des dependances)
- `lib.rs`: bootstrap Tauri + enregistrement des commandes

## Mapping MVC

- Model: `models/*`, `repositories/*`
- View: frontend Vue existant (`neurales-web/src/pages/*`)
- Controller: `controllers/*` (commands Tauri invoques par le front)

## Flux de donnees

1. Vue appelle une commande Tauri (`invoke`).
2. Controller valide l'entree et delegue au service.
3. Service applique les regles metier.
4. Repository lit/ecrit les donnees.
5. Resultat remonte au front sous forme de DTO.

## Etat actuel du squelette

- Patients exposes en commandes:
  - `list_patients`
  - `get_patient_by_id`
  - `create_patient`
  - `delete_patient`
- Persistance temporaire: repository in-memory.

## Prochaine etape recommandee

1. Remplacer le repository in-memory par SQLite.
2. Ajouter modules `devices`, `results`, `sessions` avec le meme pattern.
3. Creer une couche TypeScript `desktopClient` qui route vers `invoke` en desktop.
