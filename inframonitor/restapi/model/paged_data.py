from dataclasses import dataclass


@dataclass
class PagedData:
    limit: int
    offset: int
    order: str
    count: int
