#!/usr/bin/env python3
"""Read-only status view for every OfficeHub Compose profile."""

from __future__ import annotations

import json
import subprocess
import sys

COMPOSE = [
    "docker", "compose",
    "-f", "compose.yaml",
    "-f", "compose.apps.yaml",
    "--profile", "*",
]


def command(*args: str) -> str:
    result = subprocess.run(
        [*COMPOSE, *args], text=True, capture_output=True, check=False
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"Docker Compose exited with {result.returncode}")
    return result.stdout


def parse_ps(output: str) -> list[dict]:
    """Support both JSON arrays and newline-delimited Compose JSON objects."""
    data = output.strip()
    if not data:
        return []
    try:
        parsed = json.loads(data)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return [json.loads(line) for line in data.splitlines() if line.strip()]


def classification(item: dict | None) -> tuple[str, str, bool]:
    if item is None:
        return "○", "Not created", False

    state = str(item.get("State") or "").lower()
    health = str(item.get("Health") or "").lower()
    exit_code = item.get("ExitCode")
    if state == "running":
        if health == "unhealthy":
            return "✘", "Unhealthy", True
        if health == "starting":
            return "◌", "Starting (healthcheck)", False
        if health == "healthy":
            return "✔", "Healthy", False
        return "✔", "Running", False
    if state == "exited":
        if str(exit_code) == "0":
            return "✔", "Completed", False
        return "✘", f"Error (exit {exit_code})", True
    if state == "dead":
        return "✘", "Error (dead)", True
    if state in {"created", "restarting", "paused", "removing"}:
        return "○", state.capitalize(), False
    return "○", state.capitalize() if state else "Unknown", False


def main() -> int:
    try:
        configured = [name.strip() for name in command("config", "--services").splitlines() if name.strip()]
        found = parse_ps(command("ps", "-a", "--format", "json"))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Cannot read OfficeHub Docker status: {exc}", file=sys.stderr)
        return 2

    by_service: dict[str, list[dict]] = {}
    for container in found:
        service = str(container.get("Service") or "")
        if service:
            by_service.setdefault(service, []).append(container)

    lines = []
    failures = 0
    for service in configured:
        containers = by_service.get(service) or [None]
        for container in containers:
            icon, label, failed = classification(container)
            failures += int(failed)
            name = str(container.get("Name") or service) if container else service
            lines.append((icon, f"Container {name}", label))

    width = max((len(name) for _, name, _ in lines), default=0)
    for icon, name, label in lines:
        print(f" {icon} {name:<{width}}  {label}")
    print(f"\n{len(configured)} configured services · {failures} failed/unhealthy")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
