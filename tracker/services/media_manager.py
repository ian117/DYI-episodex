from typing import Optional

from db.database import Database
from models.title import Title


class MediaManager:
    def __init__(self, db: Database):
        self._db = db

    # ── Títulos ─────────────────────────────────────────────────────────────

    def add(self, title: Title) -> int:
        sql = """
            INSERT INTO titles
                (title, type, season, episode, status, rating, platform, notes, watched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            title.title, title.type, title.season, title.episode,
            title.status, title.rating, title.platform,
            title.notes, title.watched_at,
        )
        cursor = self._db.execute(sql, params)
        self._db.commit()
        return cursor.lastrowid

    def update(self, title: Title) -> None:
        sql = """
            UPDATE titles SET
                title=?, type=?, season=?, episode=?,
                status=?, rating=?, platform=?, notes=?, watched_at=?
            WHERE id=?
        """
        params = (
            title.title, title.type, title.season, title.episode,
            title.status, title.rating, title.platform,
            title.notes, title.watched_at, title.id,
        )
        self._db.execute(sql, params)
        self._db.commit()

    def delete(self, id: int) -> None:
        self._db.execute("DELETE FROM titles WHERE id=?", (id,))
        self._db.commit()

    def get_all(self, filters: dict = None) -> list[Title]:
        sql = "SELECT * FROM titles WHERE 1=1"
        params = []

        if filters:
            if filters.get('type'):
                sql += " AND type=?"
                params.append(filters['type'])
            if filters.get('status'):
                sql += " AND status=?"
                params.append(filters['status'])
            if filters.get('platform'):
                sql += " AND platform=?"
                params.append(filters['platform'])

        sql += " ORDER BY title COLLATE NOCASE ASC"
        cursor = self._db.execute(sql, params)
        return [self._row_to_title(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int) -> Optional[Title]:
        cursor = self._db.execute("SELECT * FROM titles WHERE id=?", (id,))
        row = cursor.fetchone()
        return self._row_to_title(row) if row else None

    def search(self, query: str) -> list[Title]:
        pattern = f"%{query}%"
        sql = "SELECT * FROM titles WHERE title LIKE ? COLLATE NOCASE ORDER BY title COLLATE NOCASE ASC"
        cursor = self._db.execute(sql, (pattern,))
        return [self._row_to_title(row) for row in cursor.fetchall()]

    def _row_to_title(self, row) -> Title:
        return Title(
            id=row['id'],
            title=row['title'],
            type=row['type'],
            status=row['status'],
            season=row['season'],
            episode=row['episode'],
            rating=row['rating'],
            platform=row['platform'],
            notes=row['notes'],
            watched_at=row['watched_at'],
        )

    # ── Tipos ────────────────────────────────────────────────────────────────

    def get_types(self) -> list[str]:
        cursor = self._db.execute("SELECT name FROM types ORDER BY name")
        return [row['name'] for row in cursor.fetchall()]

    def get_types_full(self) -> list[dict]:
        cursor = self._db.execute("SELECT id, name FROM types ORDER BY name")
        return [{'id': row['id'], 'name': row['name']} for row in cursor.fetchall()]

    def add_type(self, name: str) -> int:
        cursor = self._db.execute("INSERT INTO types (name) VALUES (?)", (name.strip(),))
        self._db.commit()
        return cursor.lastrowid

    def rename_type(self, id: int, name: str) -> None:
        self._db.execute("UPDATE types SET name=? WHERE id=?", (name.strip(), id))
        self._db.commit()

    def count_titles_with_type(self, name: str) -> int:
        cursor = self._db.execute("SELECT COUNT(*) FROM titles WHERE type=?", (name,))
        return cursor.fetchone()[0]

    def delete_type(self, id: int) -> None:
        self._db.execute("DELETE FROM types WHERE id=?", (id,))
        self._db.commit()

    # ── Estados ──────────────────────────────────────────────────────────────

    def get_statuses(self) -> list[str]:
        cursor = self._db.execute("SELECT name FROM statuses ORDER BY name")
        return [row['name'] for row in cursor.fetchall()]

    def get_statuses_full(self) -> list[dict]:
        cursor = self._db.execute("SELECT id, name FROM statuses ORDER BY name")
        return [{'id': row['id'], 'name': row['name']} for row in cursor.fetchall()]

    def add_status(self, name: str) -> int:
        cursor = self._db.execute("INSERT INTO statuses (name) VALUES (?)", (name.strip(),))
        self._db.commit()
        return cursor.lastrowid

    def rename_status(self, id: int, name: str) -> None:
        self._db.execute("UPDATE statuses SET name=? WHERE id=?", (name.strip(), id))
        self._db.commit()

    def count_titles_with_status(self, name: str) -> int:
        cursor = self._db.execute("SELECT COUNT(*) FROM titles WHERE status=?", (name,))
        return cursor.fetchone()[0]

    def delete_status(self, id: int) -> None:
        self._db.execute("DELETE FROM statuses WHERE id=?", (id,))
        self._db.commit()

    # ── Plataformas ──────────────────────────────────────────────────────────

    def get_platforms(self) -> list[str]:
        cursor = self._db.execute("SELECT name FROM platforms ORDER BY name")
        return [row['name'] for row in cursor.fetchall()]

    def get_platforms_full(self) -> list[dict]:
        cursor = self._db.execute("SELECT id, name FROM platforms ORDER BY name")
        return [{'id': row['id'], 'name': row['name']} for row in cursor.fetchall()]

    def add_platform(self, name: str) -> int:
        cursor = self._db.execute("INSERT INTO platforms (name) VALUES (?)", (name.strip(),))
        self._db.commit()
        return cursor.lastrowid

    def rename_platform(self, id: int, name: str) -> None:
        self._db.execute("UPDATE platforms SET name=? WHERE id=?", (name.strip(), id))
        self._db.commit()

    def count_titles_with_platform(self, name: str) -> int:
        cursor = self._db.execute("SELECT COUNT(*) FROM titles WHERE platform=?", (name,))
        return cursor.fetchone()[0]

    def delete_platform(self, id: int) -> None:
        self._db.execute("DELETE FROM platforms WHERE id=?", (id,))
        self._db.commit()
