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


@app.get("/players/{player_id}/territory_battles")
def get_battles_by_player(player_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT tb.territory_battle_id, tb.player_id, p.name, tb.phase, tb.territory_points, tb.undeployed_gp, tb.checked_at
        FROM territory_battles tb
        JOIN players p ON p.player_id = tb.player_id
        WHERE tb.player_id = %s
        ORDER BY tb.territory_battle_id DESC
        """,
        (player_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "territory_battle_id": r[0],
            "player_id": r[1],
            "player_name": r[2],
            "phase": r[3],
            "territory_points": r[4],
            "undeployed_gp": r[5],
            "checked_at": r[6].isoformat() if r[6] else None,
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

# ------------------------------
# Territory battle APIs
# ------------------------------


class TerritoryBattleCreate(BaseModel):
    player_id: int
    phase: int | None = None
    territory_points: int | None = None
    undeployed_gp: int | None = None


class TerritoryBattleUpdate(BaseModel):
    territory_battle_id: int
    phase: int | None = None
    territory_points: int | None = None
    undeployed_gp: int | None = None


@app.get("/territory_battles")
def get_territory_battles():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT territory_battle_id, player_id, phase, territory_points, undeployed_gp, checked_at FROM territory_battles ORDER BY territory_battle_id DESC")
    rows = cur.fetchall()

    conn.close()

    return [
        {
            "territory_battle_id": r[0],
            "player_id": r[1],
            "phase": r[2],
            "territory_points": r[3],
            "undeployed_gp": r[4],
            "checked_at": r[5].isoformat() if r[5] else None,
        }
        for r in rows
    ]


@app.get("/territory_battles/joined")
@app.get("/territory_battles/joined/")
def get_territory_battles_joined(player_id: int | None = None):
    conn = get_conn()
    cur = conn.cursor()

    if player_id is not None:
        cur.execute(
            """
            SELECT tb.territory_battle_id, tb.player_id, p.name, tb.phase, tb.territory_points, tb.undeployed_gp, tb.checked_at
            FROM territory_battles tb
            JOIN players p ON p.player_id = tb.player_id
            WHERE tb.player_id = %s
            ORDER BY tb.territory_battle_id DESC
            """,
            (player_id,)
        )
    else:
        cur.execute(
            """
            SELECT tb.territory_battle_id, tb.player_id, p.name, tb.phase, tb.territory_points, tb.undeployed_gp, tb.checked_at
            FROM territory_battles tb
            JOIN players p ON p.player_id = tb.player_id
            ORDER BY tb.territory_battle_id DESC
            """
        )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "territory_battle_id": r[0],
            "player_id": r[1],
            "player_name": r[2],
            "phase": r[3],
            "territory_points": r[4],
            "undeployed_gp": r[5],
            "checked_at": r[6].isoformat() if r[6] else None,
        }
        for r in rows
    ]


@app.get("/territory_battles/{territory_battle_id}")
def get_territory_battle(territory_battle_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT territory_battle_id, player_id, phase, territory_points, undeployed_gp, checked_at FROM territory_battles WHERE territory_battle_id = %s", (territory_battle_id,))
    row = cur.fetchone()

    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Territory battle not found")

    return {
        "territory_battle_id": row[0],
        "player_id": row[1],
        "phase": row[2],
        "territory_points": row[3],
        "undeployed_gp": row[4],
        "checked_at": row[5].isoformat() if row[5] else None,
    }


@app.post("/territory_battles")
def create_territory_battle(tb: TerritoryBattleCreate):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO territory_battles (player_id, phase, territory_points, undeployed_gp)
            VALUES (%s, %s, %s, %s)
            RETURNING territory_battle_id, checked_at
            """,
            (tb.player_id, tb.phase, tb.territory_points, tb.undeployed_gp)
        )

        row = cur.fetchone()
        conn.commit()

        return {
            "territory_battle_id": row[0],
            "checked_at": row[1].isoformat() if row[1] else None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@app.put("/territory_battles")
def update_territory_battle(tb: TerritoryBattleUpdate):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE territory_battles
        SET phase = COALESCE(%s, phase),
            territory_points = COALESCE(%s, territory_points),
            undeployed_gp = COALESCE(%s, undeployed_gp)
        WHERE territory_battle_id = %s
        """,
        (tb.phase, tb.territory_points, tb.undeployed_gp, tb.territory_battle_id)
    )

    if cur.rowcount == 0:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=404, detail="Territory battle not found")

    conn.commit()
    conn.close()

    return {"success": True}


@app.delete("/territory_battles/{territory_battle_id}")
def delete_territory_battle(territory_battle_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM territory_battles WHERE territory_battle_id = %s", (territory_battle_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Territory battle not found")

    return {"success": True}