# Budget-Tracker

Requires Python 3.11+ and Docker Desktop. Run commands from the project folder.

## Setup

### Windows (PowerShell)

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### macOS / Linux

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The remaining commands are the same on both systems with the virtual environment active.

Create `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5440/budget_tracker_db
```

## Database and demo data

```sh
docker compose up -d
docker compose exec db pg_isready -U postgres -d budget_tracker_db
```

Wait until the check reports `accepting connections`, then run:

```sh
python seed.py
```

Run `seed.py` once: it creates tables and inserts demo data.

## Run the app

```sh
python -m uvicorn main:app --reload
```

## Run tests

```sh
python -m pytest
```

## API documentation

[Swagger UI](http://localhost:8000/docs)
