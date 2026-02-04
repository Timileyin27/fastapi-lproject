from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema,app.utils
import app.models

router = APIRouter(
        prefix="/users",
    tags=["Users"]
)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=app.schema.UserOut)
def create_user(new_user:app.schema.UserCreate, db:Session=Depends(get_db)):
      hashed_password=app.utils.hash_password(new_user.password)
      user = app.models.User(
        email=new_user.email,
        password=hashed_password,
        role= new_user.role
    )
      db.add(user)
      db.commit()
      db.refresh(user)
      return user
@router.get("/{id}", response_model=app.schema.UserOut)
def get_user(id:int, db:Session=Depends(get_db)):
    user = db.query(app.models.User).filter(app.models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    return user