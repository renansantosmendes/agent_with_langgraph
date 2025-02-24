from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from study_files.architectures.service_controller_repository.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            # Log the exception or handle it accordingly
            print(f"Error fetching user: {e}")
            return None

    def create_user(self, name: str, email: str):
        try:
            user = User(name=name, email=email)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            # Log the exception or handle it accordingly
            print(f"Error creating user: {e}")
            self.db.rollback()
            return None

    def delete_user(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
            return user
        except SQLAlchemyError as e:
            # Log the exception or handle it accordingly
            print(f"Error deleting user: {e}")
            self.db.rollback()
            return None
