# OfficeHub

A local-first freelancer office starter: Nuxt 4 + Nuxt UI dashboard, FastAPI + PostgreSQL records, and Ollama + Open WebUI for self-hosted AI.

## Quick start

1. Install Docker Engine and Docker Compose v2.
2. Install [just](https://github.com/casey/just) and Python 3 (for local secret generation).
3. Run `just bootstrap` to generate `.env` with independent random credentials, validate Docker Compose and launch the stack.
4. Run `just open` to launch the frontend dashboard in your default browser (uses `OFFICEHUB_PORT` from `.env`).
5. Visit **http://localhost:3000** for OfficeHub and **http://localhost:3001** for Open WebUI.
6. Register the first Open WebUI admin account locally. After registration, set `ENABLE_SIGNUP: "false"` under `openwebui.environment` and run `docker compose up -d --force-recreate openwebui` to prevent additional sign-ups. Do not expose the initial registration endpoint publicly.

Model download runs in the one-off `ollama-init` container (default `llama3.2:1b`); first boot can take a while. Check progress with `docker compose logs -f ollama-init`. To load another model, change `OLLAMA_MODEL` in `.env` and run `docker compose up --force-recreate ollama-init`.

## Services

| Compose service | Purpose | Host access |
| --- | --- | --- |
| `frontend` | Nuxt UI dashboard and same-origin API proxy | 127.0.0.1:3000 |
| `api` | FastAPI CRUD + dashboard aggregates | Docker network only |
| `postgres` | Persistent clients, projects, tasks and invoices | Docker network only |
| `ollama` | Local LLM inference | Docker network only |
| `ollama-init` | One-shot model pull | No HTTP port |
| `openwebui` | AI chat UI (own login and storage) | 127.0.0.1:3001 |

Compose creates persistent named volumes for database, Ollama models and Open WebUI. Ports are bound to loopback for local usage. Access from remote machines requires TLS, authentication and a properly configured reverse proxy; do not simply publish these ports.

### Functional starter features

- Dashboard counts, recent tasks, unpaid invoice totals and Ollama connectivity/model status.
- Client, project, task and invoice list/create/delete backed by PostgreSQL.
- A same-origin Nuxt server proxy to FastAPI; the backend and database are not directly published.
- Optional project/client relationships by numeric ID. Invoices are **records only**, not legally compliant invoice documents or a payment processor.
- AI chat via Open WebUI, independent from the application records.

### Project layout

```text
compose.yaml
.env.example
backend/
  Dockerfile
  requirements.txt
  app/main.py
frontend/
  Dockerfile
  package.json
  nuxt.config.ts
  app/
    app.vue
    components/OfficeShell.vue
    pages/index.vue
    pages/[section].vue
    assets/css/main.css
  server/api/[...path].ts
```

## Commands (justfile)

Run `just` or `just --list` to discover recipes. Start with `just bootstrap` (first-time setup), `just open` (browser), and `just init` (generate missing `.env`). All Docker-backed recipes have the `docker-` prefix: `just docker-check`, `just docker-up`, `just docker-start`, `just docker-stop`, `just docker-down`, `just docker-restart`, `just docker-build`, `just docker-pull`, `just docker-upgrade`, `just docker-ps`, `just docker-logs api`, `just docker-smoke`, `just docker-db-shell`, `just docker-db-backup`, `just docker-db-restore backups/<name>.sql.gz`, `just docker-model-pull`, `just docker-models`, `just docker-model llama3.2:3b`, and `just docker-chat`.

Database backups are written to `backups/` (ignored by Git); restore only to an empty or properly prepared database to avoid conflicts. `just docker-down` preserves volumes; **do not** use `docker compose down -v` unless you intend to delete stored data.

### update-cli support

The root-level `update-cli.yaml` is a [r14r/update-cli](https://github.com/r14r/update-cli) schema-v2 manifest, **not** a GitHub Actions workflow. It declares `setup` (generate environment if absent, build/start stack), `ci` (validate Compose) and `run` (`just docker-start`). Configure the repository/branch in update-cli's own project configuration, for example:

```bash
update-cli init officehub --mode pull --repository https://github.com/r14r/OfficeHub.git
update-cli config --set source.ref=main
update-cli setup
update-cli run
```

`just update-check`, `just update-plan`, `just update`, `just update-doctor` and `just update-status` wrap installed update-cli commands. **Changing to `main` only works after the feature branch has been merged.** If deploying the feature branch before merge, set `source.ref=feature/officehub-compose-starter` instead. Do not commit update-cli's local state/config or application backup directories.

## Start all applications and open the dashboard

```bash
just start-all       # generate secrets, build/start every optional app, then frontend
just start-frontend  # build/start only the OfficeHub frontend and its dependencies
just open            # open the dashboard in your default browser
```

`just start-all` can consume substantial RAM, CPU, disk and startup time. Some optional apps still need upstream-specific first-run setup. The dashboard lists configured application URLs and per-app Overview pages; URLs are not availability checks. Nuxt receives public URLs from Compose via `NUXT_PUBLIC_*_URL`, using ports from `.env`. Gotenberg and Qdrant remain private API-only services.

## Optional application services

See [docs/apps.md](docs/apps.md) for 31 optional component definitions (Paperless-ngx, Gotenberg, n8n, DocuSeal, Kimai, Authentik, Stirling PDF, Vikunja, Twenty, Actual Budget, Qdrant, Akaunting, Invoice Ninja, and Automatisch) and their separate PostgreSQL/MySQL/Redis dependencies. Each app is activated through its own Compose profile, uses `officehub-<repo>-<service>` names, and writes persistent data to `../data/officehub-<repo>-<service>/`.

```bash
just apps-init
just docker-app-check
just docker-app-up documents
just docker-app-up automation
just docker-app-down documents
```

The extra applications are **not** automatically enabled with `just bootstrap`; they are independent installations. Dify is intentionally delegated to its official upstream Compose distribution because its generated multi-service dependencies are significantly more involved. The existing core services retain their original Docker volumes to prevent accidental data loss; migrate those volumes explicitly if moving to bind mounts.

## Development

For API work: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`. Without `DATABASE_URL`, the API uses a local SQLite file for development. For frontend work: `cd frontend && npm install && npm run dev`. Set `NUXT_API_INTERNAL_URL=http://localhost:8000` for local frontend development. Keep Docker's database and AI services running if needed.

API endpoints: `GET /health`, `GET /api/dashboard`, and `GET/POST /api/{clients|projects|tasks|invoices}`, `DELETE /api/{resource}/{id}`. FastAPI's autogenerated docs are available inside the Docker network at `http://api:8000/docs`.

## Production hardening checklist

This repository is a **starter**, not a deployed production office system. **There is no application user authentication or authorization**. Do not expose it publicly or store sensitive client data until this is addressed. Add a user identity provider, per-user/tenant authorization checks, TLS, database migrations (Alembic), schema constraints and edit workflows, backups and restore drills, monitoring, invoice numbering/tax requirements, audit logs, and tests. Pin images/dependency versions and review container updates. The example secrets must be changed before launch. Existing Postgres volumes are not reconfigured automatically when changing database credentials.

**Backend naming:** This uses **FastAPI** (Python API framework), not `fastai` (machine-learning library), because the office dashboard needs a web API. fastai can be introduced as an optional analytics/ML worker later.

## Shared Ollama and application navigation

The sidebar has three top-level groups: **Dashboard**, **Admin** (Ollama), and **Apps** (one item per configured application). Visit `/admin/ollama` for online status, installed models, and init commands. The main dashboard retains client, project, task, and invoice shortcuts.

There is **exactly one Ollama server**, `ollama`, with its persisted `ollama_data` volume and internal endpoint `http://ollama:11434`. Do not add independent Ollama containers for other applications.

| App | Init job | Model configuration |
| --- | --- | --- |
| Open WebUI | `officehub-openwebui-ollama-init` | `OPENWEBUI_OLLAMA_MODEL` (falls back to `OLLAMA_MODEL`) |
| n8n | `officehub-n8n-ollama-init` (automation profile) | `N8N_OLLAMA_MODEL` |

Both jobs wait for the same Ollama service and pull their configured model into the same store. Pulls are idempotent; if both request the same model it is shared, not duplicated. Run `just docker-model-pull` for Open WebUI or `just docker-n8n-model-pull` for n8n. In n8n, set the Ollama node credential's base URL to `http://ollama:11434`; merely downloading a model does not create n8n workflows or credentials.

The other optional office applications have no demonstrated Ollama dependency, so no artificial initializer jobs have been added to them.

## Container logs and Docker volumes

Application stdout/stderr is collected by Docker's container logging system; inspect it using `docker compose logs` or `just docker-app-logs <profile>`. It does **not** require application-specific log bind mounts. A scan of both Compose manifests found only one filesystem log mount, Stirling PDF's `/logs`. That directory is now backed by the named Docker volume `officehub_stirlingpdf_logs` rather than `../data/officehub-stirlingpdf-frontend/logs`, avoiding cloud-synced host filesystem `chown` failures.

The other application data bind mounts are unchanged. Existing files in the old Stirling PDF log folder are **not automatically migrated**; copy them separately if needed. Docker-managed volumes persist across `docker compose down`, but are removed by `docker compose down -v` or an explicit volume deletion.

## Stirling PDF: cloud-directory mount workaround

Stirling PDF uses named Docker volumes for **all three** writable directories:
`officehub_stirlingpdf_config:/configs`, `officehub_stirlingpdf_logs:/logs`, and `officehub_stirlingpdf_tessdata:/usr/share/tessdata`.
This prevents macOS Docker Desktop from trying to create and chown those paths under the cloud-synced `../data` folder.

**Migration warning:** existing files in `../data/officehub-stirlingpdf-frontend/config` or `tessdata` are **not automatically copied** into Docker-managed volumes. Back them up and migrate them before starting the new configuration if they hold custom settings or OCR language data. Other services' host bind mounts are unchanged; they may still encounter permissions errors on a cloud-synced filesystem. For database health failures, inspect the individual container logs rather than treating the Stirling volume change as a database fix.

## Database persistence on macOS / cloud folders

Optional application databases now use named Docker volumes rather than `../data` bind mounts, to avoid `chown: Permission denied` on synchronized filesystems. **Existing host database contents are not automatically migrated**; read [database volume migration notes](docs/database-volumes.md) before starting services with existing data.

## Full stack status

Run `just status` to inspect all core and optional-profile Compose services, including stopped or never-created containers. The output uses a concise progress-like list with ✓/✘/○ icons, service/container name, current state, and Docker health when available. One-off initialization jobs that exited successfully are shown as **Completed**; failures are marked **Error**.

```bash
just status
```

This command **does not start or recreate containers**. The status is a snapshot: historical build events like `Built` and `Recreated` cannot be recovered from `docker compose ps`. It reads Docker Compose JSON output and may return a nonzero status when a container is failed or unhealthy. Use `just docker-app-logs <profile>` for diagnostic logs.
