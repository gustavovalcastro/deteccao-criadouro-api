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

- Python 3.10+
- `pip`
- [bcrypt](https://pypi.org/project/bcrypt/) (already listed in `requirements.txt`)
- PostgreSQL for production deployments (SQLite is used only for quick local testing)

## Setup

1. (Optional) create a virtual environment:
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
   DATABASE_URL=postgresql+psycopg2://user:password@host:5432/mosquito
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
- For production (PostgreSQL), use the SQL script below to create the schema before running the API.

<details>
<summary><strong>PostgreSQL schema</strong></summary>

```sql
-- Types
DROP TYPE IF EXISTS result_type CASCADE;
DROP TYPE IF EXISTS result_status CASCADE;

CREATE TYPE result_type AS ENUM ('terreno', 'propriedade');
CREATE TYPE result_status AS ENUM ('visualized', 'finished', 'processing', 'failed');

-- Mobile users
CREATE TABLE "user" (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(50)  NOT NULL,
    email    VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    phone    VARCHAR(11)  NOT NULL
);

CREATE TABLE address (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    cep           VARCHAR(8)   NOT NULL,
    street        VARCHAR(255) NOT NULL,
    number        INTEGER      NOT NULL,
    neighborhood  VARCHAR(100) NOT NULL,
    complement    VARCHAR(10),
    city          VARCHAR(100) NOT NULL,
    lat           VARCHAR(50)  NOT NULL,
    lng           VARCHAR(50)  NOT NULL
);

-- Portal administrators
CREATE TABLE user_portal (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR NOT NULL,
    email    VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    city     VARCHAR NOT NULL
);

-- Campaigns
CREATE TABLE campaign (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR NOT NULL,
    description      VARCHAR NOT NULL,
    campaignInfos    JSONB,
    instructionInfos JSONB,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    finish_at        TIMESTAMP WITH TIME ZONE,
    city             VARCHAR NOT NULL
);

-- Results
CREATE TABLE result (
    id               SERIAL PRIMARY KEY,
    campaign_id      INTEGER REFERENCES campaign(id) ON DELETE SET NULL,
    user_id          INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    original_image   VARCHAR NOT NULL,
    result_image     VARCHAR,
    type             result_type   NOT NULL,
    status           result_status NOT NULL,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    feedback_like    BOOLEAN NOT NULL DEFAULT FALSE,
    feedback_comment VARCHAR
);

CREATE INDEX ix_result_user_id ON result (user_id);
CREATE INDEX ix_result_campaign_id ON result (campaign_id);
```

</details>

## Key Endpoints (high level)

- `POST /user/createUser`  register a mobile user (password hashed with bcrypt)
- `POST /user/login` authenticate a mobile user
- `POST /userPortal/createUserPortal` register a portal administrator
- `POST /userPortal/login` authenticate a portal administrator
- `GET /campaigns/getCampaignByUser/{userId}` campaigns filtered by the user city, includes results for that user
- `GET /campaigns/getCampaignHome/{userId}` campaigns for the user city with `resultsNotDisplayed`
- `GET /campaigns/getCampaignByUserPortal/{userPortalId}` campaigns filtered by the portal admin city (no results)
- `GET /campaigns/getAllCampaigns` list every campaign with attached results
- `POST /campaigns/createCampaign` create a campaign
- `PUT /results/updateResultStatus` update the status of a detection result (accepts `{id, status}`)

Refer to the `/swagger` docs for the full contract of every route.
