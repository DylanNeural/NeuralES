from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repository_sql.organisation_repository_sql import OrganisationRepositorySQL

from app.application.dtos.organisation_dto import (
    OrganisationCreateIn,
    OrganisationUpdateIn,
    OrganisationOut,
)

from app.application.use_cases.create_organisation import CreateOrganisation
from app.application.use_cases.get_organisation import GetOrganisation
from app.application.use_cases.list_organisations import ListOrganisations
from app.application.use_cases.update_organisation import UpdateOrganisation
from app.application.use_cases.delete_organisation import DeleteOrganisation

router = APIRouter(prefix="/organisations", tags=["organisations"])

def get_repo(db: Session = Depends(get_db)) -> OrganisationRepositorySQL:
    return OrganisationRepositorySQL(db)

@router.post("", response_model=OrganisationOut, status_code=201)
def create_org(payload: OrganisationCreateIn, repo=Depends(get_repo)):
    uc = CreateOrganisation(repo)
    org = uc.execute(nom=payload.nom, org_type=payload.type, adresse=payload.adresse)
    return OrganisationOut(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )

@router.get("/{organisation_id}", response_model=OrganisationOut)
def get_org(organisation_id: int, repo=Depends(get_repo)):
    uc = GetOrganisation(repo)
    org = uc.execute(organisation_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return OrganisationOut(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )

@router.get("", response_model=list[OrganisationOut])
def list_orgs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
):
    uc = ListOrganisations(repo)
    orgs = uc.execute(limit=limit, offset=offset)
    return [
        OrganisationOut(
            organisation_id=o.organisation_id,
            nom=o.nom,
            type=o.org_type,
            adresse=o.adresse,
            created_at=o.created_at,
        )
        for o in orgs
    ]

@router.patch("/{organisation_id}", response_model=OrganisationOut)
def update_org(organisation_id: int, payload: OrganisationUpdateIn, repo=Depends(get_repo)):
    uc = UpdateOrganisation(repo)
    org = uc.execute(
        organisation_id=organisation_id,
        nom=payload.nom,
        org_type=payload.type,
        adresse=payload.adresse,
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return OrganisationOut(
        organisation_id=org.organisation_id,
        nom=org.nom,
        type=org.org_type,
        adresse=org.adresse,
        created_at=org.created_at,
    )

@router.delete("/{organisation_id}", status_code=204)
def delete_org(organisation_id: int, repo=Depends(get_repo)):
    uc = DeleteOrganisation(repo)
    ok = uc.execute(organisation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return None
