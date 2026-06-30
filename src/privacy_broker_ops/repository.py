from __future__ import annotations

import csv
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from .models import Exposure, ExposureCreate, ExposureStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS exposures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    broker_id TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    data_type TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    discovered_at TEXT NOT NULL,
    last_contact_at TEXT
);

CREATE TABLE IF NOT EXISTS mail_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exposure_id INTEGER NOT NULL,
    direction TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY(exposure_id) REFERENCES exposures(id)
);
"""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class Repository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def init(self) -> None:
        with self.connect() as con:
            con.executescript(SCHEMA)

    def add_exposure(self, item: ExposureCreate) -> int:
        with self.connect() as con:
            cur = con.execute(
                """
                INSERT INTO exposures (broker_id, url, status, data_type, note, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (item.broker_id, item.url, item.status.value, item.data_type, item.note, utc_now()),
            )
            return int(cur.lastrowid)

    def list_exposures(self) -> list[Exposure]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM exposures ORDER BY id DESC").fetchall()
        return [self._row_to_exposure(row) for row in rows]

    def get_exposure(self, exposure_id: int) -> Exposure:
        with self.connect() as con:
            row = con.execute("SELECT * FROM exposures WHERE id = ?", (exposure_id,)).fetchone()
        if row is None:
            raise ValueError(f"Exposure introuvable: {exposure_id}")
        return self._row_to_exposure(row)

    def mark_prepared(self, exposure_id: int) -> None:
        self.update_status(exposure_id, ExposureStatus.DEMANDE_PREPAREE)

    def mark_sent(self, exposure_id: int) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE exposures SET status = ?, last_contact_at = ? WHERE id = ?",
                (ExposureStatus.ENVOYE.value, utc_now(), exposure_id),
            )

    def update_status(self, exposure_id: int, status: ExposureStatus) -> None:
        with self.connect() as con:
            con.execute("UPDATE exposures SET status = ? WHERE id = ?", (status.value, exposure_id))

    def export_csv(self, out: Path) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        rows = self.list_exposures()
        with out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "broker_id",
                "url",
                "status",
                "data_type",
                "discovered_at",
                "last_contact_at",
                "note",
            ])
            for row in rows:
                writer.writerow([
                    row.id,
                    row.broker_id,
                    row.url,
                    row.status.value,
                    row.data_type,
                    row.discovered_at,
                    row.last_contact_at or "",
                    row.note,
                ])

    @staticmethod
    def _row_to_exposure(row: sqlite3.Row) -> Exposure:
        return Exposure(
            id=int(row["id"]),
            broker_id=str(row["broker_id"]),
            url=str(row["url"]),
            status=ExposureStatus(str(row["status"])),
            data_type=str(row["data_type"]),
            note=str(row["note"]),
            discovered_at=str(row["discovered_at"]),
            last_contact_at=row["last_contact_at"],
        )
