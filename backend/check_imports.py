#!/usr/bin/env python
"""
Script de test pour vérifier les imports et la structure.
"""

import sys
from pathlib import Path

# Ajouter le backend au Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("Vérification structure NeuralES Backend")
print("=" * 60)

try:
    print("\n✓ Importation config...")
    from app.config import settings
    print(f"  - App: {settings.app_name}")
    print(f"  - Database: {settings.database_url[:50]}...")

    print("\n✓ Importation domain entities...")
    from app.domain.entities.organisation import Organisation

    print("\n✓ Importation ports...")
    from app.application.ports.organisation_repository import OrganisationRepository

    print("\n✓ Importation use cases...")
    from app.application.use_cases.create_organisation import CreateOrganisation
    from app.application.use_cases.get_organisation import GetOrganisation
    from app.application.use_cases.list_organisations import ListOrganisations
    from app.application.use_cases.update_organisation import UpdateOrganisation
    from app.application.use_cases.delete_organisation import DeleteOrganisation

    print("\n✓ Importation repositories...")
    from app.data.repositories.organisation_repository import OrganisationRepositorySQLImpl

    print("\n✓ Importation core...")
    from app.core.eeg_processor import EEGProcessor

    print("\n✓ Importation API schemas...")
    from app.api.schemas import (
        OrganisationCreateRequest,
        OrganisationUpdateRequest,
        OrganisationResponse,
        EEGStreamPayload,
    )

    print("\n✓ Importation API routes...")
    from app.api.routes import organisations_router, eeg_router, health_router

    print("\n✓ Importation main app...")
    from app.main import app

    print("\n" + "=" * 60)
    print("✓ SUCCÈS : Tous les imports sont valides!")
    print("=" * 60)
    print("\nProchaines étapes:")
    print("  1. Installer les dépendances: pip install -r requirements.txt")
    print("  2. Configurer .env (copier depuis .env.example)")
    print("  3. Lancer: uvicorn app.main:app --reload")
    print("  4. Accéder à http://localhost:8000/docs pour la documentation API")
    print()

except Exception as e:
    print(f"\n✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
