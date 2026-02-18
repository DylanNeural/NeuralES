from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepository:
    """Acces DB pour les refresh tokens."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, jti: str, user_id: int, issued_at: datetime, expires_at: datetime) -> RefreshTokenModel:
        token = RefreshTokenModel(
            jti=jti,
            user_id=user_id,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.commit()
        return token

    def get_by_jti(self, jti: str) -> RefreshTokenModel | None:
        return self.db.get(RefreshTokenModel, jti)

    def get_active_by_jti(self, jti: str) -> RefreshTokenModel | None:
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.jti == jti,
            RefreshTokenModel.revoked_at.is_(None),
            RefreshTokenModel.expires_at > datetime.utcnow(),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token: RefreshTokenModel, replaced_by_jti: str | None = None) -> None:
        token.revoked_at = datetime.utcnow()
        token.replaced_by_jti = replaced_by_jti
        self.db.commit()
