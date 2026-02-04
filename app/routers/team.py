from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema
import app.models,app.oauth2
from typing import Optional,List
router = APIRouter(
        prefix="/teams",
    tags=["Teams"]
)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=app.schema.TeamOut)
def create_team(new_team:app.schema.TeamCreate, db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user)):
      team = app.models.Team(owner_id=current_user.id,**new_team.dict())
      db.add(team)
      db.commit()
      db.refresh(team)
      return team
@router.get("/", response_model=List[app.schema.TeamOut])
def get_teams(db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user),limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    teams = db.query(app.models.Team).filter(app.models.Team.owner_id == current_user.id,app.models.Team.name.contains(search)).limit(limit).offset(skip).all()
    return teams

@router.get("/{id}", response_model=app.schema.TeamOut)
def get_teams(id:int,db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user),limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    team = db.query(app.models.Team).filter(app.models.Team.id == id,app.models.Team.owner_id == current_user.id,app.models.Team.name.contains(search)).limit(limit).offset(skip).first()
    if not team:
         raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=f"team with {id} not found")
    return team
@router.patch("/{id}",response_model=app.schema.TeamOut)
def edit_team(id:int, updated_team:app.schema.TeamCreate, db:Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.require_admin)):
     team_query=db.query(app.models.Team).filter(app.models.Team.id == id)
     team =team_query.first()
     if team == None:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"team with {id} not found" )
     if team.owner_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
     team_query.update(updated_team.dict(),synchronize_session=False)
     db.commit()
     return team
@router.delete(
    "/{id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None  
)
def delete_team(
    id: int,
    db: Session = Depends(app.database.get_db),
    current_user: app.models.User = Depends(app.oauth2.require_admin) 
):
    team_query = db.query(app.models.Team).filter(app.models.Team.id == id)
    team = team_query.first()
   

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {id} not found"
        )
    if team.owner_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    team_query.delete(synchronize_session=False)
    db.commit()
    return
@router.post("/{id}/members",status_code=status.HTTP_201_CREATED,response_model=app.schema.TeamMemberRespone)
def add_members(id: int,payload:app.schema.TeamMemeberRequest,db: Session=Depends(get_db),current_user: app.models = Depends(app.oauth2.get_current_user)):
    team=db.query(app.models.Team).filter(app.models.Team.id == id).first()
  

    if not team:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,detail="team not found")
    if team.owner_id != current_user.id:
        raise  HTTPException (status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user= db.query(app.models.User).filter(app.models.User.id==payload.user_id).first()
  
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    existing_member = db.query(app.models.TeamMembers).filter(
    app.models.TeamMembers.user_id == payload.user_id,
    app.models.TeamMembers.team_id == id
).first()

    if existing_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a team member")
    new_member= app.models.TeamMembers(user_id=payload.user_id, team_id=id,role="member")
   
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member
@router.get("/{id}/members",response_model=List[app.schema.TeamMemberRespone])
def get_teamMember(id:int,db: Session=Depends(get_db),current_user:app.models = Depends(app.oauth2.get_current_user)):
    team_member= db.query(app.models.TeamMembers).filter(app.models.TeamMembers.team_id== id).all()
    return team_member
@router.post("/{id}/invite",status_code=status.HTTP_201_CREATED,response_model=app.schema.TeamInviteOut)
def create_invite(id:int,payload:app.schema.TeamInviteCreate,db: Session=Depends(get_db),current_user:app.models.User=Depends(app.oauth2.get_current_user)):
     team = db.query(app.models.Team).filter(app.models.Team.id == id).first()
     if not team:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="team not found")
     membership= db.query(app.models.TeamMembers).filter(app.models.TeamMembers.team_id==id,app.models.TeamMembers.user_id==current_user.id).first()
     if not  membership or membership.role=="owner":
         raise HTTPException(status_code=403, detail="Only owner can invite")
     existing_member = db.query(app.models.TeamMembers).filter(
    app.models.TeamMembers.user_id == payload.user_id,
    app.models.TeamMembers.team_id == id).first()

     if existing_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a team member")
     existing_invite= db.query(app.models.TeamInvitation).filter(app.models.TeamInvitation.team_id==id,app.models.TeamInvitation.invitee_user_id==payload.user_id,app.models.TeamInvitation.status==app.models.InvitationStatus.pending).first()
     if existing_invite:
        raise HTTPException(status_code=400, detail="Invitation already sent")
     invitation=app.models.TeamInvitation(team_id=id,invitee_user_id=payload.user_id)
     db.add(invitation)
     db.commit()
     db.refresh(invitation)
     return invitation 