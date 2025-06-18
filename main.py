from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database init
def init_db():
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vk_user_id TEXT UNIQUE,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class ProgressData(BaseModel):
    vk_user_id: str
    completed: bool

@app.post("/save_progress")
def save_progress(data: ProgressData):
    try:
        conn = sqlite3.connect("db.sqlite")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO players (vk_user_id, completed)
            VALUES (?, ?)
            ON CONFLICT(vk_user_id) DO UPDATE SET completed=excluded.completed
        ''', (data.vk_user_id, int(data.completed)))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_players")
def get_players():
    try:
        conn = sqlite3.connect("db.sqlite")
        cursor = conn.cursor()
        cursor.execute('SELECT vk_user_id, completed FROM players')
        rows = cursor.fetchall()
        conn.close()
        return [{"vk_user_id": row[0], "completed": bool(row[1])} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))