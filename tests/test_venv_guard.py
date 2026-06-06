import sys
import unittest
from unittest.mock import patch

from src import venv_guard


class VenvGuardTests(unittest.TestCase):
    def test_ensure_virtualenv_passes_for_project_venv(self) -> None:
        self.assertTrue(venv_guard._VENV_DIR.is_dir())
        venv_guard.ensure_virtualenv()

    def test_ensure_virtualenv_fails_without_virtualenv(self) -> None:
        with (
            patch.object(sys, "prefix", "/usr"),
            patch.object(sys, "base_prefix", "/usr"),
            self.assertRaises(SystemExit),
        ):
            venv_guard.ensure_virtualenv()

    def test_ensure_virtualenv_fails_for_foreign_virtualenv(self) -> None:
        with (
            patch.object(sys, "prefix", "/tmp/other-venv"),
            patch.object(sys, "base_prefix", "/usr"),
            self.assertRaises(SystemExit),
        ):
            venv_guard.ensure_virtualenv()


if __name__ == "__main__":
    unittest.main()
