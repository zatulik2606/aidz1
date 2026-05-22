from datetime import UTC, datetime
from pathlib import Path
import sqlite3


def resolve_leads_db_path(leads_db_path: str) -> Path:
    normalized = (leads_db_path or "./data/leads.db").strip() or "./data/leads.db"
    return Path(normalized)


def ensure_leads_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            request_text TEXT NOT NULL,
            source_chat_id INTEGER
        )
        """
    )


def save_lead(
    *,
    name: str,
    contact: str,
    request_text: str,
    source_chat_id: int | None,
    leads_db_path: str,
) -> None:
    db_path = resolve_leads_db_path(leads_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        ensure_leads_schema(connection)
        connection.execute(
            """
            INSERT INTO leads (created_at, name, contact, request_text, source_chat_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(UTC).isoformat(),
                name,
                contact,
                request_text,
                source_chat_id,
            ),
        )
        connection.commit()
