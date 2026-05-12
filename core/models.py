from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    rank: int
    name: str
    price: str
    price_usd: float
    thumbnail: str
    product_url: str
    platform: str
    rating: Optional[float] = None
    reviews: Optional[int] = None
    sales: Optional[str] = None


@dataclass
class ScrapeResult:
    category: str
    scraped_at: str
    platforms: dict = field(default_factory=dict)
