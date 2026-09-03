from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import *

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/companies")
async def all_games(cur=Depends(get_database_cursor)):
    cur.execute("SELECT * FROM companies;")
    return cur.fetchone()