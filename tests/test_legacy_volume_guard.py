"""Safety tests for legacy bind-mount preflight checks."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "legacy-volume-guard.py"
spec = importlib.util.spec_from_file_location("legacy_guard", FILE)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def test_empty_directories_are_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "officehub-test"
            folder.mkdir()
            self.assertEqual(guard.populated_paths([{"legacy": "officehub-test"}], Path(td)), [])

    def test_existing_files_trigger_block(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "officehub-test"
            folder.mkdir()
            (folder / "state.json").write_text("important")
            self.assertEqual(len(guard.populated_paths([{"legacy": "officehub-test"}], Path(td))), 1)

    def test_missing_directories_do_not_block(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(guard.populated_paths([{"legacy": "missing"}], Path(td)), [])

    def test_profile_filtering(self):
        all_entries = guard.legacy_entries()
        docs = guard.legacy_entries("documents")
        self.assertTrue(docs)
        self.assertTrue(all(row["profile"] == "documents" for row in docs))
        self.assertGreater(len(all_entries), len(docs))


if __name__ == "__main__":
    unittest.main()
