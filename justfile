# OfficeHub development and deployment commands.
# Requirements: just, Docker Engine + Docker Compose v2, Python 3 for init/open.
set dotenv-load := true

default:
    @just --list

# One-time setup: generate secrets, validate Compose, and launch the stack.
bootstrap: init docker-up

# Open the frontend dashboard in the default browser (macOS/Linux/Windows).
open:
    @python3 -c 'import os, webbrowser; url="http://localhost:"+os.environ.get("OFFICEHUB_PORT", "3000"); print("Opening", url); webbrowser.open(url)'

# Generate a local .env with secure random secrets (does not overwrite).
init:
    @if [ -f .env ]; then echo ".env already exists; leaving it unchanged"; else \
      cp .env.example .env; \
      python3 -c 'from pathlib import Path; import secrets; p=Path(".env"); t=p.read_text().replace("replace-with-a-long-random-password", secrets.token_hex(32)).replace("replace-with-a-random-64-character-hex-string", secrets.token_hex(32)); p.write_text(t)'; \
      chmod 600 .env; \
      echo "Created .env with generated local secrets"; \
    fi

# Ensure configuration and secrets are ready for Docker Compose.
docker-check-env:
    @test -f .env || { echo "Missing .env — run: just init"; exit 1; }
    @! grep -Eq '^(POSTGRES_PASSWORD|WEBUI_SECRET_KEY)=replace-' .env || { echo "Change example secrets in .env"; exit 1; }
    @docker compose config --quiet

# Validate the Compose file (after creating .env).
docker-check: docker-check-env
    @echo "Docker Compose configuration is valid"

# Build and start the full stack.
docker-up: docker-check-env
    docker compose up --build -d

# Start existing images without rebuilding.
docker-start: docker-check-env
    docker compose up -d

# Stop containers while preserving persistent data.
docker-stop:
    docker compose stop

# Stop and remove containers; keep named volumes.
docker-down:
    docker compose down

# Restart the stack.
docker-restart: docker-check-env
    docker compose restart

# Build application images.
docker-build: docker-check-env
    docker compose build api frontend

# Pull published service images (Ollama, PostgreSQL, Open WebUI).
docker-pull: docker-check-env
    docker compose pull --ignore-buildable

# Pull fresh service images, rebuild application images, restart.
docker-upgrade: docker-check-env
    docker compose pull --ignore-buildable
    docker compose up -d --build

# Show service state.
docker-ps:
    docker compose ps

# Follow all logs, or specify a service: just docker-logs api.
docker-logs service="":
    docker compose logs --tail=100 -f {{service}}

# Check backend health through the frontend proxy.
docker-smoke:
    curl --fail --show-error --silent http://localhost:${OFFICEHUB_PORT:-3000}/api/dashboard

# Show all configured services.
docker-services:
    docker compose config --services

# Open a shell in the backend.
docker-api-shell:
    docker compose exec api sh

# Open PostgreSQL CLI.
docker-db-shell:
    docker compose exec postgres sh -c 'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# Create a timestamped SQL backup in ./backups.
docker-db-backup:
    @mkdir -p backups
    @docker compose exec -T postgres sh -c 'exec pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "backups/officehub-$(date +%Y%m%d-%H%M%S).sql.gz"
    @echo "Backup saved in backups/"

# Restore a SQL dump into an EMPTY PostgreSQL database. This can overwrite data.
docker-db-restore file:
    @test -f {{quote(file)}} || { echo "File does not exist"; exit 1; }
    @echo "Restoring into the configured database; existing objects may conflict"
    gzip -dc {{quote(file)}} | docker compose exec -T postgres sh -c 'exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# Download the configured Ollama model.
docker-model-pull: docker-check-env
    docker compose up --force-recreate ollama-init

# List models in Ollama.
docker-models:
    docker compose exec ollama ollama list

# Pull an arbitrary Ollama model: just docker-model llama3.2:3b
docker-model name:
    docker compose exec ollama ollama pull {{quote(name)}}

# Open a local Ollama chat: just docker-chat llama3.2:1b
docker-chat name="llama3.2:1b":
    docker compose exec ollama ollama run {{quote(name)}}

# View installed CLI versions.
versions:
    @docker --version
    @docker compose version
    @just --version
    @python3 --version

# Test the configured update-cli source for new releases (requires update-cli).
update-check:
    update-cli check

# Preview a transactional update (requires update-cli).
update-plan:
    update-cli update --plan

# Deploy an update using the configured update-cli project (requires update-cli).
update:
    update-cli update

# Validate update-cli's local project configuration.
update-doctor:
    update-cli doctor

# Inspect update-cli deployment status.
update-status:
    update-cli status

# Run update-cli setup tasks from update-cli.yaml.
update-setup:
    update-cli setup

# Generate independent secrets for the optional application profiles.
apps-init: init
    python3 scripts/init-apps.py

# Start optional app profile (and its dependencies); e.g. just docker-app-up documents.
docker-app-up profile: apps-init
    docker compose -f compose.yaml -f compose.apps.yaml --profile {{quote(profile)}} up -d

# Stop only services from the selected profile, preserving all data and core services.
docker-app-down profile:
    @services="$(docker compose -f compose.yaml -f compose.apps.yaml --profile {{quote(profile)}} config --services | grep '^officehub-' || true)"; if [ -z "$services" ]; then echo "No optional services found"; exit 1; fi; docker compose -f compose.yaml -f compose.apps.yaml stop $services

# Follow optional application logs; e.g. just docker-app-logs automation.
docker-app-logs profile:
    docker compose -f compose.yaml -f compose.apps.yaml --profile {{quote(profile)}} logs -f --tail=100

# Validate all optional app definitions and their secret references.
docker-app-check: apps-init
    docker compose -f compose.yaml -f compose.apps.yaml config --quiet
