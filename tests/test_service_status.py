"""Unit tests for the fast read-only Docker status CLI."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / "scripts" / "service-status.py"
spec = importlib.util.spec_from_file_location("service_status", FILE)
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


class StatusTests(unittest.TestCase):
    def test_one_shot_completed_but_persistent_exited_is_failure(self):
        item = {"State": "exited", "Status": "Exited (0) 2 minutes ago"}
        self.assertEqual(status.state_of(item, one_shot=True), ("✔", "Completed", False))
        self.assertEqual(status.state_of(item), ("✘", "Stopped (exit 0)", True))

    def test_restarting_is_not_healthy(self):
        self.assertEqual(status.state_of({"State": "restarting", "Status": "Restarting"}), ("✘", "Restarting", True))

    def test_unhealthy_is_failure(self):
        self.assertEqual(status.state_of({"State": "running", "Status": "Up 1m (unhealthy)"}), ("✘", "Unhealthy", True))

    def test_not_created_is_visible(self):
        self.assertEqual(status.state_of(None), ("○", "Not created", False))

    def test_timeout_is_bounded(self):
        with patch.object(status.subprocess, "run", side_effect=subprocess.TimeoutExpired("docker", 12)) as run:
            with self.assertRaisesRegex(RuntimeError, "12s"):
                status.inspect_containers("officehub")
            self.assertEqual(run.call_args.kwargs["timeout"], 12)

    def test_project_name_env_and_dotenv(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "compose.yaml").write_text("name: officehub\n")
            (root / ".env").write_text("COMPOSE_PROJECT_NAME=custom_project\n")
            with patch.object(status, "ROOT", root):
                with patch.dict(status.os.environ, {}, clear=True):
                    self.assertEqual(status.project_name(), "custom_project")
                with patch.dict(status.os.environ, {"COMPOSE_PROJECT_NAME": "env_project"}):
                    self.assertEqual(status.project_name(), "env_project")
                self.assertEqual(status.project_name("explicit_project"), "explicit_project")


if __name__ == "__main__":
    unittest.main()
