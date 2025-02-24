from repository import UserRepository
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self, user_id: int):
        user = self.repository.get_user(user_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        return user

    def create_user(self, name: str, email: str):
        # Regra de negócio: impedir emails duplicados
        if self.repository.db.query(UserRepository).filter_by(email=email).first():
            raise ValueError("E-mail já cadastrado.")
        return self.repository.create_user(name, email)

    def delete_user(self, user_id: int):
        user = self.repository.delete_user(user_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        return user
