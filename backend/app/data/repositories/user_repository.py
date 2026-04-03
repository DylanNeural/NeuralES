from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.models.user_model import UserModel


class UserRepository:
    """Acces DB pour les utilisateurs"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.db.get(UserModel, user_id)

    def update_last_login(self, user: UserModel) -> None:
        user.last_login_at = datetime.utcnow()
        self.db.commit()
