from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Title:
    id: Optional[int]
    title: str
    type: str       # "series" | "movie"
    status: str     # "watching" | "completed" | "pending"
    season: Optional[int] = None
    episode: Optional[int] = None
    rating: Optional[int] = None
    platform: Optional[str] = None
    notes: Optional[str] = None
    watched_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
