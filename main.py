from fastapi import FastAPI
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/players")
def players():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    data = cur.fetchall()
    conn.close()
    return data