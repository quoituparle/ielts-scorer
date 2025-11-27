import os
from dotenv import load_dotenv

from fastapi import  Depends, HTTPException, status, APIRouter
from sqlmodel import Session
from sqladmin import Admin, BaseView, expose
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.applications import Starlette

from ..database import get_db, engine
from ..auth.views import get_user, authenticate_user
from ..models import UserAdmin, TopicAdmin

load_dotenv()

router = APIRouter(prefix="/admin", tags=["Admin App"])

def make_admin(db: Session, email: str):
    admin_email = os.getenv('admin_email')

    update_user = get_user(db, email)

    if update_user.is_superuser == True:
        return
    else:
        update_user.is_superuser

    try:
        db.add(update_user)
        db.commit()
        db.refresh(update_user)
    except Exception as e:
        db.rollback()
        print(f"Unable to update admin user, {e}")


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["email"], form["password"]

        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            user = authenticate_user(db=db, email=email, password=password)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if user.is_superuser is not True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your not a admin user")

        request.session.update({
            "token": os.getenv("token"),
            "is_superuser": True 
            })
        return True


    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True
 
authentication_backend = AdminAuth(secret_key=os.getenv('secret_key'))
