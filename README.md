# Detecção Criadouro API (Breeding Site Detection API)

This backend project aims to integrate the frontend systems of both the mobile and web applications and the system (algorithm) for detecting potential breeding. This work is part of the Final Project for the Computer Engineering course at Pontifícia Universidade Católica de Minas Gerais(PUC-MG).

# Technical Information

REST API built with FastAPI, SQLAlchemy, and Pydantic to support the portal web and mobile app. It exposes endpoints for managing users (mobile and portal administrators), campaigns, and processing detection results.

## Project Structure

```
deteccaomosquito/
|-- app/
|   |-- config.py
|   |-- database.py
|   |-- main.py
|   |-- models/
|   |   |-- campaign.py
|   |   |-- user.py
|   |   `-- userPortal.py
|   |-- routers/
|   |   |-- campaign.py
|   |   |-- user.py
|   |   `-- userPortal.py
|   |-- schemas/
|   |   |-- campaign.py
|   |   |-- user.py
|   |   `-- userPortal.py
|   `-- services/
|       |-- campaign_service.py
|       |-- user_service.py
|       `-- userPortal_service.py
|-- requirements.txt
`-- README.md
```

## Requirements

- Python 3.13+
- `pip`

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the environment:
   - Windows PowerShell:
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in the `.env` file. Examples:
   ```bash
   # SQLite (dev only)
   DATABASE_URL=sqlite:///./meubanco.db

   # PostgreSQL (production)
   DATABASE_URL=<check on Notion 'Configurações de Ambiente' page>
   ```

## Running the API

Start the FastAPI server with Uvicorn:
```bash
uvicorn app.main:app --reload
```

Once running, the API documentation is available at `http://localhost:8000/swagger`.

## Security Notes

- User and portal passwords are stored using bcrypt hashes (`UserService` / `UserPortalService`).
- E-mail addresses are unique within their respective tables (`user.email` and `user_portal.email`).

## Database Notes

- Tables are generated automatically on startup when using SQLAlchemy migrations in development.

## Key Endpoints (high level)

Refer to the `/swagger` docs for the full contract of every route.
