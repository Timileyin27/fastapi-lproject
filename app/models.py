from app.database import Base,get_db
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy import Enum
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,default='now()')
    role= Column(String, nullable=False, default="User")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,default='now()')
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invitations = relationship("TeamInvitation", back_populates="team")


class Task (Base):
    __tablename__="tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,default='now()')
class TeamMembers (Base):
    __tablename__ = "team_members"
    user_id= Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    role= Column(String, nullable=False, default="User")
    joined_at=Column(TIMESTAMP(timezone=True), nullable=False,default='now()')

class InvitationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class TeamInvitation(Base):
    __tablename__ = "team_invitations"
    id = Column(Integer, primary_key=True, nullable=False)

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )



    invitee_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )


    status = Column(
        Enum(InvitationStatus),
        server_default="pending",
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )
    team = relationship("Team", back_populates="invitations")
    invitee = relationship("User")
