# Runbook — deployment & operations

This runbook covers running EMBEDHUNT AI locally, in Docker, and on Kubernetes,
plus database migrations and common operational tasks.

## Configuration

All configuration is environment-driven. Copy the template and edit values:

```powershell
Copy-Item backend/.env.example backend/.env
```

Key variables:

| Variable          | Purpose                                            |
| ----------------- | -------------------------------------------------- |
| `DATABASE_URL`    | Async SQLAlchemy URL (asyncpg for Postgres)        |
| `SECRET_KEY`      | JWT signing secret — **must** be set in production |
| `BCRYPT_ROUNDS`   | Password hashing cost (default sane)               |
| `REDIS_URL`       | Cache / rate-limit backend                         |
| `ENVIRONMENT`     | `development` / `production`                        |

> Never commit a real `.env`. Generate `SECRET_KEY` with a CSPRNG and store it in a
> secret manager (Kubernetes Secret, cloud secret store).

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements/base.txt -r backend/requirements/test.txt
python scripts/init_db.py        # SQLite tables
python scripts/seed.py           # seed companies
cd backend
uvicorn app.main:app --reload
```

Smoke test:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Database migrations (Alembic)

Run from `backend/`:

```powershell
# Apply latest schema
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Roll back one revision
alembic downgrade -1
```

`migrations/env.py` reads `DATABASE_URL` from settings and registers all models, so
autogenerate sees the full metadata. For quick local resets, `scripts/init_db.py`
creates tables directly without migrations (development only).

## Docker (local stack)

```powershell
docker compose -f deployment/docker/docker-compose.yml up --build
```

This starts `db` (postgres:16), `redis` (7), and `api` with healthchecks. The API
image is multi-stage (`deployment/docker/Dockerfile.backend`), runs as a non-root
user, and serves with gunicorn + uvicorn workers.

## Kubernetes

```powershell
kubectl apply -f deployment/kubernetes/
```

Manifests (apply order matches filenames):

| File                      | Resource                                   |
| ------------------------- | ------------------------------------------ |
| `00-namespace.yaml`       | Namespace                                  |
| `01-config.yaml`          | ConfigMap + Secret template                |
| `02-api-deployment.yaml`  | Deployment (3 replicas) + Service + probes |
| `03-hpa.yaml`             | HorizontalPodAutoscaler (3→20, 70% CPU)    |
| `04-ingress.yaml`         | Ingress with TLS via cert-manager          |

Before applying, populate the Secret in `01-config.yaml` with real values
(`SECRET_KEY`, `DATABASE_URL`, etc.). Never store production secrets in plain
manifests committed to git — use a sealed-secrets / external-secrets controller.

### Health & readiness

- Liveness: `GET /health`
- Readiness: `GET /health/ready` (checks DB connectivity)

Both are wired into the Deployment probes.

## Observability

- Prometheus scrape config: `deployment/monitoring/prometheus.yml` (targets
  `/metrics`).
- Reverse proxy, rate limiting, and security headers: `deployment/nginx/nginx.conf`.

Key metrics: `embedhunt_http_requests_total` (by method/route/status) and the
request-latency histogram.

## Tests

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
```

CI runs the same suite plus a Docker image build on every push / PR
(`.github/workflows/ci.yml`).

## Common issues

| Symptom                              | Likely cause / fix                                    |
| ------------------------------------ | ----------------------------------------------------- |
| `401` on protected routes            | Missing/expired token — re-login or refresh           |
| Readiness failing                    | DB unreachable — check `DATABASE_URL` and the db pod  |
| Migration autogenerate empty         | Models not imported — verify `migrations/env.py`      |
| Mobile can't reach API on emulator   | Use `http://10.0.2.2:8000`, not `localhost`           |
