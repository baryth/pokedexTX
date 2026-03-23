# Pokedex API

A minimalist REST API for Pokedex and Trainer management built with Python and FastAPI.

## Stack

- **FastAPI** — web framework
- **SQLite** — persistent storage (via stdlib `sqlite3`)
- **CSV** — pokemon data source (stdlib `csv`)
- **Uvicorn** — ASGI server

## Project Structure

```
pokedex_api/
├── main.py          # Application entry point
├── pokedex.csv      # Pokemon data source
├── pokedex.db       # SQLite database (auto-generated)
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Place your `pokedex.csv` in the project folder with the following headers:

```
ID,Name,Type,Total,HP,Attack,Defense,Sp. Atk,Sp. Def,Speed
```

## Run

```bash
python main.py
```

Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

### Pokemons (read-only)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/pokemons` | List all pokemons |
| `GET` | `/pokemons/{id}` | Get a pokemon by ID |

### Trainers (CRUD)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/trainers` | Create a new trainer |
| `GET` | `/trainers` | List all trainers |
| `DELETE` | `/trainers/{id}` | Delete a trainer by ID |

### Trainer request body

```json
{
  "id": 1,
  "name": "Ash",
  "city": "Pallet Town"
}
```

## Notes

- Pokemon data is loaded from `pokedex.csv` into SQLite on first startup.
- Returns `404 Not Found` if a pokemon or trainer ID does not exist.
- No authentication required.
