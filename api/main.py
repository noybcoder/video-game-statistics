from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import analytics

app = FastAPI()
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