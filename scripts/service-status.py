#!/usr/bin/env python3
"""Fast, read-only OfficeHub status using a single bounded Docker Engine query."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 12
ONE_SHOT_SERVICES = frozenset({
    "officehub-openwebui-ollama-init",
    "officehub-n8n-ollama-init",
})


def declared_services(filename: str) -> list[str]:
    names = []
    in_services = False
    for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
        if line == "services:":
            in_services = True
            continue
        if in_services and line and not line.startswith((" ", "#")):
            break
        if in_services:
            match = re.match(r"^  ([a-zA-Z0-9][a-zA-Z0-9_.-]*):(?:\s|$)", line)
            if match:
                names.append(match.group(1))
    return names


def project_name(override: str | None = None) -> str:
    if override:
        return override
    if os.environ.get("COMPOSE_PROJECT_NAME"):
        return os.environ["COMPOSE_PROJECT_NAME"]
    env_file = ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*COMPOSE_PROJECT_NAME\s*=\s*(.*?)\s*$", line)
            if match:
                name = match.group(1).strip().strip("'\"")
                if name:
                    return name
    for line in (ROOT / "compose.yaml").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^name:\s*(\S+)\s*$", line)
        if match:
            return match.group(1).strip("'\"")
    return ROOT.name.lower()


def inspect_containers(project: str) -> list[dict]:
    args = [
        "docker", "ps", "--all",
        "--filter", f"label=com.docker.compose.project={project}",
        "--format", "{{json .}}",
    ]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Docker did not respond within {TIMEOUT_SECONDS}s; "
            "check Docker Desktop or run 'docker info'"
        ) from exc
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "docker ps failed")
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def state_of(item: dict | None, *, one_shot: bool = False) -> tuple[str, str, bool]:
    if item is None:
        return "○", "Not created", False
    state = str(item.get("State") or "").lower()
    status = str(item.get("Status") or "")
    if state == "running":
        if "(unhealthy)" in status.lower():
            return "✘", "Unhealthy", True
        if "(health: starting)" in status.lower():
            return "◌", "Starting (healthcheck)", False
        if "(healthy)" in status.lower():
            return "✔", "Healthy", False
        return "✔", "Running", False
    if state == "exited":
        code = re.search(r"Exited \((\d+)\)", status, re.IGNORECASE)
        exit_code = int(code.group(1)) if code else None
        if exit_code == 0 and one_shot:
            return "✔", "Completed", False
        if exit_code == 0:
            return "✘", "Stopped (exit 0)", True
        return "✘", f"Error (exit {exit_code})" if code else "Exited", True
    if state == "dead":
        return "✘", "Error (dead)", True
    if state == "restarting":
        return "✘", "Restarting", True
    if state in {"created", "paused", "removing"}:
        return "○", state.capitalize(), True
    return "✘", state.capitalize() if state else "Unknown", True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="Override the Compose project name")
    args = parser.parse_args()
    try:
        names = list(dict.fromkeys(
            declared_services("compose.yaml") + declared_services("compose.apps.yaml")
        ))
        containers = inspect_containers(project_name(args.project))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Cannot read OfficeHub Docker status: {exc}", file=sys.stderr)
        return 2

    grouped: dict[str, list[dict]] = {}
    for container in containers:
        labels = str(container.get("Labels") or "")
        match = re.search(r"(?:^|,)com\.docker\.compose\.service=([^,]+)", labels)
        if match and match.group(1) in names:
            grouped.setdefault(match.group(1), []).append(container)

    rows = []
    failures = 0
    for service in names:
        for item in grouped.get(service) or [None]:
            symbol, state, failed = state_of(item, one_shot=service in ONE_SHOT_SERVICES)
            failures += int(failed)
            container_name = str(item.get("Names") or service) if item else service
            rows.append((symbol, f"Container {container_name}", state))
    width = max((len(name) for _, name, _ in rows), default=0)
    for symbol, name, state in rows:
        print(f" {symbol} {name:<{width}}  {state}", flush=True)
    print(f"\n{len(names)} configured services · {failures} failed/inactive")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
