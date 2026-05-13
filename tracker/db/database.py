import os
import sys
import sqlite3


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'tracker.db')


class Database:
    def __init__(self):
        self._path = get_db_path()
        self._conn: sqlite3.Connection = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        self._conn = sqlite3.connect(self._path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS titles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                type        TEXT    NOT NULL,
                season      INTEGER,
                episode     INTEGER,
                status      TEXT    NOT NULL DEFAULT 'Pendiente',
                rating      INTEGER,
                platform    TEXT,
                notes       TEXT,
                watched_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS types (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            INSERT OR IGNORE INTO types (name) VALUES
                ('Serie'), ('Película');

            CREATE TABLE IF NOT EXISTS statuses (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            INSERT OR IGNORE INTO statuses (name) VALUES
                ('Pendiente'), ('Viendo'), ('Completado');

            CREATE TABLE IF NOT EXISTS platforms (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            INSERT OR IGNORE INTO platforms (name) VALUES
                ('Netflix'), ('HBO Max'), ('Disney+'), ('Amazon Prime'),
                ('Apple TV+'), ('Crunchyroll'), ('Paramount+'), ('YouTube'),
                ('Otra');
        """)
        self._conn.commit()
        self._run_migrations()

    def _run_migrations(self) -> None:
        # Migrar valores internos antiguos a nombres de display
        self._conn.execute("UPDATE titles SET type='Serie' WHERE type='series'")
        self._conn.execute("UPDATE titles SET type='Película' WHERE type='movie'")
        self._conn.execute("UPDATE titles SET status='Pendiente' WHERE status='pending'")
        self._conn.execute("UPDATE titles SET status='Viendo' WHERE status='watching'")
        self._conn.execute("UPDATE titles SET status='Completado' WHERE status='completed'")
        self._conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._conn.execute(sql, params)

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
