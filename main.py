from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqlmodel import Session

from .auth import views as auth_views
from .core import views as main_views
from .admin import admin as admin_app
from .admin.admin import authentication_backend, make_admin 
from .models import UserAdmin, TopicAdmin
from .database import engine, get_db, create_db_and_tables 
import os

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

admin = Admin(templates_dir="my_templates", app=app, engine=engine, authentication_backend=authentication_backend)
# change view function in sqladmin have conflict, cannot change the existing page
admin.add_view(UserAdmin)
admin.add_view(TopicAdmin)

@app.on_event("startup")
def on_startup():
    # 1. 先建表
    create_db_and_tables()
    
    print("Checking admin user...")
    db_gen = get_db()
    db = next(db_gen) 
    try:
        make_admin(db, email=os.getenv('admin_email'))
    except Exception as e:
        print(f"Error setting up admin: {e}")
    finally:
        db.close()