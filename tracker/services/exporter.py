import csv
import json
from dataclasses import asdict

from models.title import Title


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
