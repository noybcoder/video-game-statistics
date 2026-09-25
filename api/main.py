from contextlib import asynccontextmanager
from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from config.database import init_connection_pool, close_connection_pool
from api.routes import analytics

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_connection_pool(settings.get_database_connection_string)
    yield
    close_connection_pool()

app = FastAPI(lifespan=lifespan)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return [
        "What is the most popular genre?",
        "What genre does each developer/company specialize in?",
        "What game engines are most developers using?",
        "What is the most popular game engine for each platform?",
        "What is the most popular game engine for each genre?"
    ]