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
    update_user = get_user(db, email)

    update_user.is_superuser = True

    try:
        db.add(update_user)
        db.commit()
        db.refresh(update_user)
    except Exception as e:
        db.rollback()
        print(f"Unable to update admin user, {e}")
db_session = next(get_db()) # next() function is vital because the get_db() use yield, next() can activate yield to continue passing.

make_admin(db_session, email=os.getenv('admin_email'))

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, db: Session = Depends(get_db)) -> bool:
        form = await request.form()
        email, password = form["email"], form["password"]

        user = authenticate_user(db=db, email=email, password=password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        request.session.update({"token": os.getenv('token')})

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
