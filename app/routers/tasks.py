from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema
import app.models,app.oauth2
from typing import Optional,List
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)
@router.post ("/", response_model=app.schema.TaskOut)
def create_task(new_task:app.schema.TaskCreate,db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user)):
    task= app.models.Task( owner_id = current_user.id, **new_task.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
@router.get ("/",response_model=List[app.schema.TaskOut])
def get_task(db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user),limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    teams= db.query(app.models.Task).filter(app.models.Task.owner_id==current_user.id, app.models.Task.title.contains(search)).limit(limit).offset(skip)
    return teams
@router.get ("/{id}",response_model=app.schema.TaskOut)
def get_task(id:int,db: Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user),limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    task= db.query(app.models.Task).filter(app.models.Task.id ==id,app.models.Task.owner_id==current_user.id,app.models.Task.title.contains(search)).limit(limit).offset(skip).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id {id} is not found")
    return task
@router.patch("/{id}",response_model=app.schema.TaskOut)
def edit_task(id:int, updated_task:app.schema.TaskCreate,db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user)):
    task_query= db.query(app.models.Task).filter(app.models.Task.id==id)
    task= task_query.first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id {id} is not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="you are unautorized")
    task_query.update(updated_task.dict(),synchronize_session=False)
    db.commit()
    return task 
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT,response_model=None)
def delete_task(id:int,db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user)):
    task_query= db.query(app.models.Task).filter(app.models.Task.id==id)
    task= task_query.first()
    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id {id} is not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="you are unautorized")
    task_query.delete(synchronize_session=False)
    db.commit()
    return None