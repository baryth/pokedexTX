import csv
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_PATH = "pokedex.db"
CSV_PATH = "pokedex.csv"

app = FastAPI(title="Pokedex API", description="Read-only Pokedex + Trainer CRUD", version="1.0.0")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pokemons (
                id      INTEGER PRIMARY KEY,
                name    TEXT    NOT NULL,
                type    TEXT,
                total   INTEGER,
                hp      INTEGER,
                attack  INTEGER,
                defense INTEGER,
                sp_atk  INTEGER,
                sp_def  INTEGER,
                speed   INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                id   INTEGER PRIMARY KEY,
                name TEXT    NOT NULL,
                city TEXT
            )
        """)
        conn.commit()


def load_csv_to_db():
    if not Path(CSV_PATH).exists():
        print(f"Warning: {CSV_PATH} not found — skipping Pokemon data load.")
        return

    with get_db() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM pokemons").fetchone()[0]
        if existing:
            return  # already loaded

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    int(row["ID"]),
                    row["Name"],
                    row["Type"],
                    int(row["Total"]),
                    int(row["HP"]),
                    int(row["Attack"]),
                    int(row["Defense"]),
                    int(row["Sp. Atk"]),
                    int(row["Sp. Def"]),
                    int(row["Speed"]),
                )
                for row in reader
            ]

        conn.executemany(
            "INSERT OR IGNORE INTO pokemons VALUES (?,?,?,?,?,?,?,?,?,?)", rows
        )
        conn.commit()
        print(f"Loaded {len(rows)} pokemon(s) from {CSV_PATH}.")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()
    load_csv_to_db()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class Pokemon(BaseModel):
    id: int
    name: str
    type: str | None
    total: int | None
    hp: int | None
    attack: int | None
    defense: int | None
    sp_atk: int | None
    sp_def: int | None
    speed: int | None


class TrainerCreate(BaseModel):
    id: int
    name: str
    city: str | None = None


class Trainer(BaseModel):
    id: int
    name: str
    city: str | None


# ---------------------------------------------------------------------------
# Pokemon endpoints (read-only)
# ---------------------------------------------------------------------------

@app.get("/pokemons", response_model=list[Pokemon], tags=["Pokemons"])
def list_pokemons():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM pokemons ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.get("/pokemons/{id}", response_model=Pokemon, tags=["Pokemons"])
def get_pokemon(id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM pokemons WHERE id = ?", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Pokemon {id} not found.")
    return dict(row)


# ---------------------------------------------------------------------------
# Trainer endpoints (CRUD)
# ---------------------------------------------------------------------------

@app.post("/trainers", response_model=Trainer, status_code=201, tags=["Trainers"])
def create_trainer(trainer: TrainerCreate):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM trainers WHERE id = ?", (trainer.id,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail=f"Trainer {trainer.id} already exists.")
        conn.execute(
            "INSERT INTO trainers (id, name, city) VALUES (?, ?, ?)",
            (trainer.id, trainer.name, trainer.city),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM trainers WHERE id = ?", (trainer.id,)).fetchone()
    return dict(row)


@app.get("/trainers", response_model=list[Trainer], tags=["Trainers"])
def list_trainers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM trainers ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.delete("/trainers/{id}", status_code=204, tags=["Trainers"])
def delete_trainer(id: int):
    with get_db() as conn:
        row = conn.execute("SELECT id FROM trainers WHERE id = ?", (id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Trainer {id} not found.")
        conn.execute("DELETE FROM trainers WHERE id = ?", (id,))
        conn.commit()