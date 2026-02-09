from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.organisation_repository import OrganisationRepositorySQLImpl

from app.api.schemas.organisation import (
    OrganisationCreateRequest,
    OrganisationUpdateRequest,
    OrganisationResponse,
)

from app.application.use_cases.create_organisation import CreateOrganisation
from app.application.use_cases.get_organisation import GetOrganisation
from app.application.use_cases.list_organisations import ListOrganisations
from app.application.use_cases.update_organisation import UpdateOrganisation
from app.application.use_cases.delete_organisation import DeleteOrganisation

router = APIRouter(prefix="/organisations", tags=["organisations"])


def get_repo(db: Session = Depends(get_db)) -> OrganisationRepositorySQLImpl:
    return OrganisationRepositorySQLImpl(db)


@router.post("", response_model=OrganisationResponse, status_code=201)
def create_organisation(
    payload: OrganisationCreateRequest,
    repo=Depends(get_repo),
):
    """Créer une nouvelle organisation"""
    uc = CreateOrganisation(repo)
    org = uc.execute(nom=payload.nom, org_type=payload.type, adresse=payload.adresse)
    return OrganisationResponse(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )


@router.get("/{organisation_id}", response_model=OrganisationResponse)
def get_organisation(
    organisation_id: int,
    repo=Depends(get_repo),
):
    """Récupérer une organisation par ID"""
    uc = GetOrganisation(repo)
    org = uc.execute(organisation_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return OrganisationResponse(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )


@router.get("", response_model=list[OrganisationResponse])
def list_organisations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
):
    """Lister toutes les organisations"""
    uc = ListOrganisations(repo)
    orgs = uc.execute(limit=limit, offset=offset)
    return [
        OrganisationResponse(
            organisation_id=o.organisation_id,
            nom=o.nom,
            type=o.org_type,
            adresse=o.adresse,
            created_at=o.created_at,
        )
        for o in orgs
    ]


@router.patch("/{organisation_id}", response_model=OrganisationResponse)
def update_organisation(
    organisation_id: int,
    payload: OrganisationUpdateRequest,
    repo=Depends(get_repo),
):
    """Mettre à jour une organisation"""
    uc = UpdateOrganisation(repo)
    org = uc.execute(
        organisation_id=organisation_id,
        nom=payload.nom,
        org_type=payload.type,
        adresse=payload.adresse,
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return OrganisationResponse(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )


@router.delete("/{organisation_id}", status_code=204)
def delete_organisation(
    organisation_id: int,
    repo=Depends(get_repo),
):
    """Supprimer une organisation"""
    uc = DeleteOrganisation(repo)
    ok = uc.execute(organisation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return None
