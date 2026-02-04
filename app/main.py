from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import app.models as models
from app.database import engine
from app.routers import user, team, tasks, auth

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.router.include_router(user.router)
app.router.include_router(team.router)
app.router.include_router(tasks.router)
app.router.include_router(auth.router)