from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

# 👉 OVDE IDE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ili konkretan domen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 MODELI

class PlayerCreate(BaseModel):
    name: str
    viber: str | None = None
    discord: str | None = None

class PlayerUpdate(BaseModel):
    player_id: int
    viber: str | None = None
    discord: str | None = None

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/")
def root():
    return {"status": "ok"}
'''

@app.get("/players")
def players():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    data = cur.fetchall()
    conn.close()
    return data
'''



# 🔍 GET ALL

@app.get("/players")
def get_players():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT player_id, name, viber, discord FROM players ORDER BY player_id DESC")
    rows = cur.fetchall()

    conn.close()

    return [
        {
            "player_id": r[0],
            "name": r[1],
            "viber": r[2],
            "discord": r[3]
        }
        for r in rows
    ]


# ➕ CREATE

@app.post("/players")
def create_player(player: PlayerCreate):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO players (name, viber, discord)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO NOTHING
        RETURNING player_id
        """, (player.name, player.viber, player.discord))

        row = cur.fetchone()
        conn.commit()

        return {"player_id": row[0] if row else None}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


# ✏️ UPDATE

@app.put("/players")
def update_player(player: PlayerUpdate):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    UPDATE players
    SET viber = %s,
        discord = %s
    WHERE player_id = %s
    """, (player.viber, player.discord, player.player_id))

    conn.commit()
    conn.close()

    return {"success": True}


# ❌ DELETE

@app.delete("/players/{player_id}")
def delete_player(player_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
    conn.commit()
    conn.close()

    return {"success": True}