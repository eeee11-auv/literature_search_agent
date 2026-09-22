from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Paper:
    id: str
    title: str

    authors: list[str] = field(
        default_factory=list
    )

    year: Optional[int] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    venue: Optional[str] = None

    citation_count: int = 0
    relevance_score: Optional[float] = None
    open_access_url: Optional[str] = None
    source: Optional[str] = None