from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from .auth import views as auth_views
from .core import views as main_views
from .admin import admin as admin_app
from .admin.admin import authentication_backend
from .models import UserAdmin, TopicAdmin
from .database import engine

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5173/api/login/",
    "http://localhost:5173/api/register/",
    "http://localhost:5173/api/main/user/me",
    "http://localhost:5173/api/main/user/storage",
    "http://localhost:5173/api/main/response",
    "http://localhost:5173/api/main/user/delete",
    "http://localhost:5173/api/main/user/info"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_app.router)
app.include_router(auth_views.router)
app.include_router(main_views.router)

admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend, templates_dir="admin_templates")
admin.add_view(UserAdmin)
admin.add_view(TopicAdmin)