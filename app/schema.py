from pydantic import BaseModel, EmailStr
from typing import List, Optional,Literal

class Token(BaseModel):
    access_token: str
    token_type: str
    role:str
class TokenData(BaseModel):
    id: int | None = None
    role:str
class UserCreate (BaseModel):
    email:EmailStr
    password:str
    role: Literal["User", "Admin"] = "User"
class UserOut (BaseModel):
    id:int
    email: EmailStr
    role:str
    class config:
        orm_mode=True
class TeamCreate (BaseModel):
    name:str
class TeamOut (BaseModel):
    id:int
    name:str
    owner_id:int
    class config:
        orm_mode=True
class TaskCreate (BaseModel):
    title:str
    description:Optional[str]=None
    team_id:int
class TaskOut (BaseModel):
    id:int
    title:str
    description:Optional[str]=None
    team_id:int
    owner_id:int
    class config:
        orm_mode=True
class TeamMemeberRequest (BaseModel):
    user_id: int
class TeamMemberRespone (BaseModel):
    user_id :int
    role:str
    class config:
        orm_mode=True
class TeamInviteCreate(BaseModel):
    user_id: int


   
class TeamInviteOut(BaseModel):
    id: int
    team_id: int
    invitee_user_id: int
    status: str

    class Config:
        orm_mode = True
