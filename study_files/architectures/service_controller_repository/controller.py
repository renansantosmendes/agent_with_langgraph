from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import SessionLocal
from service import UserService

router = APIRouter()

# Dependência para injeção de sessão no banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return UserService(db).get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/users/")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    try:
        return UserService(db).create_user(name, email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return UserService(db).delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
