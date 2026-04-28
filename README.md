# Archerion

`Archerion` is a library management system built as a Django REST backend with a Next.js frontend.

## Project Map

- `backend/` - Django + DRF API for accounts, catalog, inventory, circulation, reservations, fines, reports, audit, and Swagger docs.
- `frontend/` - Next.js App Router UI for readers, staff, and admins.
- `healthcheck/` - standalone Python service that displays service availability and authenticates through the backend.
- `docs/` - project documentation, architecture notes, and roadmap.
- `nginx/` - reverse proxy template for a production-style setup.
- `docker-compose.yml` - local multi-service environment.

## Services

`docker-compose.yml` defines:

- `archerion_db` - PostgreSQL 16
- `archerion_minio` - MinIO object storage
- `archerion_migrate` - one-shot Django migrations job
- `archerion_backend` - backend API
- `archerion_frontend` - frontend app
- `pgadmin` - database admin UI
- `archerion_healthcheck` - service status dashboard

## Local Run

1. Copy env templates:
   - `compose.secrets.env.example` -> `.env`
   - `backend/.env-example` -> `backend/.env`
   - `healthcheck/.env-example` -> `healthcheck/.env` if you run the healthcheck separately
2. Fill secrets and connection settings.
3. Start the stack:

```bash
docker compose up --build
```

Main endpoints by default:

- frontend: `http://localhost:3000`
- backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/swagger/`
- pgAdmin: `http://localhost:5050`
- healthcheck: `http://localhost:8085`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

## Backend Notes

- Auth uses JWT via `djangorestframework-simplejwt`.
- Backend defaults to authenticated access and opens selected catalog endpoints publicly.
- Media storage is configured for S3-compatible storage through MinIO.
- The repository currently does not contain generated Django migration files.

## Frontend Notes

- Uses Next.js App Router.
- Public pages: `/`, `/catalog`, `/book/[id]`, `/login`, `/register`.
- Reader area: `/reader`, `/reader/loans`, `/reader/reservations`, `/reader/fines`.
- Staff area: `/staff`, `/staff/issue`, `/staff/return`.
- Admin area: `/admin`, `/admin/users`, `/admin/readers`, `/admin/books`, `/admin/loans`, `/admin/audit`.

## Docs

Start with:

- `docs/README.md`
- `docs/Информация о проекте/Archerion.md`
- `docs/Информация о проекте/Полный_план.md`

## Current Gaps

- no committed Django migrations
- no full CI quality gate in repo config
- frontend README was previously template-only
- production deployment still needs hardening and operator setup
