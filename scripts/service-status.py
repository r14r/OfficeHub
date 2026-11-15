#!/usr/bin/env python3
"""Read-only OfficeHub status with one Docker Engine call and a hard timeout."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 12


def declared_services(filename: str) -> list[str]:
    found = []
    active = False
    for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
        if line == "services:":
            active = True
            continue
        if active and line and not line.startswith((" ", "#")):
            break
        if active:
            match = re.match(r"^  ([a-zA-Z0-9][a-zA-Z0-9_.-]*):(?:\s|$)", line)
            if match:
                found.append(match.group(1))
    return found


def inspect_containers() -> list[dict]:
    args = [
        "docker", "ps", "--all",
        "--filter", "label=com.docker.compose.project=officehub",
        "--format", "{{json .}}",
    ]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Docker did not respond within {TIMEOUT_SECONDS}s; check Docker Desktop or 'docker info'"
        ) from exc
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "docker ps failed")
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def state_of(container: dict | None) -> tuple[str, str, bool]:
    if container is None:
        return "○", "Not created", False
    state = str(container.get("State") or "").lower()
    status = str(container.get("Status") or "")
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
        if code and code.group(1) == "0":
            return "✔", "Completed", False
        return "✘", f"Error (exit {code.group(1)})" if code else "Exited", True
    if state == "dead":
        return "✘", "Error (dead)", True
    return "○", state.capitalize() if state else "Unknown", False


def main() -> int:
    try:
        services = list(dict.fromkeys(
            declared_services("compose.yaml") + declared_services("compose.apps.yaml")
        ))
        containers = inspect_containers()
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Cannot read OfficeHub Docker status: {exc}", file=sys.stderr)
        return 2

    by_service: dict[str, list[dict]] = {}
    for container in containers:
        labels = str(container.get("Labels") or "")
        match = re.search(r"(?:^|,)com\.docker\.compose\.service=([^,]+)", labels)
        if match and match.group(1) in services:
            by_service.setdefault(match.group(1), []).append(container)

    rows = []
    failures = 0
    for service in services:
        for item in by_service.get(service) or [None]:
            symbol, status, failed = state_of(item)
            failures += int(failed)
            name = str(item.get("Names") or service) if item else service
            rows.append((symbol, f"Container {name}", status))
    width = max((len(name) for _, name, _ in rows), default=0)
    for symbol, name, status in rows:
        print(f" {symbol} {name:<{width}}  {status}", flush=True)
    print(f"\n{len(services)} configured services · {failures} failed/unhealthy")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
