import datetime
import uuid

from typing import List
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from sqladmin import ModelView, expose, BaseView
from starlette.requests import Request


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)

class UserLogin(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_verified: bool = Field(default=False)
    verification_code: str | None = Field(default=None, index=True)
    code_expires_at: datetime.datetime | None = Field(default=None)
    api_key: str | None = Field(default=None)
    language: str
    essays: List["Essay"] = Relationship(back_populates="author")

class Essay(SQLModel, table=True):
    essay_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="essays")
    published_date: datetime.datetime = Field(default_factory=datetime.timezone.utc)
    content: str
    score: str
    topic_id: uuid.UUID = Field(foreign_key="topic.topic_id")   
    topic: "Topic" = Relationship(back_populates="essays")



class Topic(SQLModel, table=True):
    topic_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    topic: str
    essays: List["Essay"] = Relationship(back_populates="topic")


class UserAdmin( ModelView, model=User):
    column_list = [User.id, User.full_name, User.email]
    can_create = True
    can_edit = True
    can_delete = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    identity = "user"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("is_superuser", False) 

class TopicAdmin(ModelView, model=Topic):
    column_list = [Topic.topic, Topic.topic_id]
    form_columns = [Topic.topic]
    
    def is_accessible(self, request: Request) -> bool:
        return request.session.get("is_superuser", False) 

