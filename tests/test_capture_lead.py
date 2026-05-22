import asyncio
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.leads import resolve_leads_db_path
from src.tools.capture_lead import capture_lead


class CaptureLeadTests(unittest.TestCase):
    def test_capture_lead_persists_row_in_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "leads.db"
            result = asyncio.run(
                capture_lead(
                    name="Иван",
                    contact="+79991234567",
                    request_text="Хочу консультацию",
                    source_chat_id=123456,
                    leads_db_path=str(db_path),
                )
            )

            self.assertIn("Заявка сохранена", result)
            self.assertTrue(db_path.exists())

            with sqlite3.connect(db_path) as connection:
                row = connection.execute(
                    """
                    SELECT name, contact, request_text, source_chat_id
                    FROM leads
                    ORDER BY id DESC
                    LIMIT 1
                    """
                ).fetchone()

            self.assertEqual(
                row,
                ("Иван", "+79991234567", "Хочу консультацию", 123456),
            )

    def test_resolve_leads_db_path_defaults(self) -> None:
        self.assertEqual(
            str(resolve_leads_db_path("")),
            "data/leads.db",
        )
