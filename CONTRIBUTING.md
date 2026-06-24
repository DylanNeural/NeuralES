# Contribuer à NeuralES

## Stratégie de branches

```
main          ← releases stables uniquement (tags vX.Y.Z)
  └── develop ← intégration continue (base de toutes les features)
        ├── feat/<nom>    ← nouvelle fonctionnalité
        ├── fix/<nom>     ← correction de bug
        ├── refactor/<nom>
        └── chore/<nom>   ← maintenance, CI, deps
```

**Ne jamais pousser directement sur `main` ou `develop`.** Toute modification passe par un Pull Request.

## Workflow

1. Crée ta branche depuis `develop` :
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/ma-fonctionnalite
   ```

2. Développe et commite avec le format **Conventional Commits** :
   ```
   feat(patients): add SSN duplicate check on creation
   fix(auth): prevent token reuse after logout
   chore(deps): upgrade FastAPI to 0.115
   ```

3. Pousse et ouvre un PR vers `develop` (jamais vers `main`).

4. La PR doit passer la checklist du template avant d'être mergée.

5. Merge dans `main` uniquement pour les releases, avec un tag sémantique `vX.Y.Z`.

## Conventions de code

Voir [`docs/convention.md`](docs/convention.md) pour les conventions détaillées.

### Backend
- Linter : `ruff check backend/`
- Types : `mypy backend/app --ignore-missing-imports`
- Architecture Clean : toute logique métier dans `application/use_cases/`, pas dans les routes

### Frontend
- Type check : `npm run type-check`
- Linter : `npm run lint`
- Pas de `any` TypeScript sans justification commentée

## Sécurité

- Toute route backend qui modifie des données doit vérifier `current_user["organisation_id"]`
- Ne jamais logguer de données patient (PII)
- Les credentials ne font jamais partie d'un commit (utiliser `.env`)

## Taille des PRs

Préférer des PRs petites et ciblées. Une PR ne devrait pas dépasser 400 lignes changées hors fichiers générés. Si c'est plus grand, découper en plusieurs PRs.
