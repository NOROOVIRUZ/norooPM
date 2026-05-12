import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

# 카테고리 → 영어 검색어
CATEGORY_EN = {
    "전동칫솔": "electric toothbrush",
    "마사지기": "body massager",
    "이어폰": "wireless earbuds",
    "블루투스스피커": "bluetooth speaker",
    "공기청정기": "air purifier",
    "안마기": "massage gun",
    "드라이어": "hair dryer",
    "로봇청소기": "robot vacuum",
}

HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    keyword = CATEGORY_EN.get(category, category)
    url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}&s=exact-aware-popularity-rank"
    fetcher = Fetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, stealthy_headers=True)
    except Exception as e:
        print(f"[Amazon] fetch 실패: {e}")
        return []

    products = []
    items = page.css("[data-component-type='s-search-result']")

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css("h2 a span, h2 span.a-text-normal")
            price_el = item.css(".a-price .a-offscreen")
            img_el = item.css("img.s-image")
            link_el = item.css("h2 a.a-link-normal")
            rating_el = item.css(".a-icon-star-small .a-icon-alt, i.a-icon-star .a-icon-alt")
            reviews_el = item.css("[data-csa-c-content-id*='reviews'] span, .a-size-base.s-underline-text")

            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _parse_price(price_str)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            rating_text = rating_el.get("") if rating_el else ""
            rating = float(rating_text.split(" ")[0]) if rating_text else None
            reviews_text = reviews_el.get("").replace(",", "").strip() if reviews_el else ""
            reviews = int(reviews_text) if reviews_text.isdigit() else None

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="amazon",
                    rating=rating, reviews=reviews,
                ))
        except Exception:
            continue

        time.sleep(random.uniform(0.5, 1.5))

    return products


def _parse_price(price_str: str) -> float:
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0
