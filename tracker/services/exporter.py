import csv
import json
from dataclasses import asdict

from models.title import Title


def _parse_int(value) -> int | None:
    try:
        return int(value) if value not in (None, '', 'None') else None
    except (ValueError, TypeError):
        return None


def _parse_str(value) -> str | None:
    if value in (None, '', 'None'):
        return None
    return str(value).strip() or None


class Exporter:
    def to_csv(self, titles: list[Title], path: str) -> None:
        if not titles:
            return
        fieldnames = ['id', 'title', 'type', 'season', 'episode', 'status',
                      'rating', 'platform', 'notes', 'watched_at']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in titles:
                writer.writerow(asdict(t))

    def to_json(self, titles: list[Title], path: str) -> None:
        data = [asdict(t) for t in titles]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def from_csv(self, path: str) -> list[Title]:
        titles = []
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                titles.append(self._row_to_title(row))
        return titles

    def from_json(self, path: str) -> list[Title]:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return [self._row_to_title(entry) for entry in data]

    def _row_to_title(self, row: dict) -> Title:
        return Title(
            id=None,
            title=str(row.get('title', '')).strip(),
            type=str(row.get('type', '')).strip(),
            status=str(row.get('status', '')).strip(),
            season=_parse_int(row.get('season')),
            episode=_parse_int(row.get('episode')),
            rating=_parse_int(row.get('rating')),
            platform=_parse_str(row.get('platform')),
            notes=_parse_str(row.get('notes')),
            watched_at=_parse_str(row.get('watched_at')),
        )
