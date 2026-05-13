import re
import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    url = f"https://www.amazon.co.jp/s?k={category}&s=relevanceblender"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Amazon JP] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Amazon JP] 실패: {e}")
        return []

    products = []
    items = page.css("[data-component-type='s-search-result']")
    print(f"[Amazon JP] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("h2 span").get("").strip()
            price_str = item.css(".a-price .a-offscreen").get("").strip()
            thumbnail = item.css("img.s-image").attrib.get("src", "")
            href = item.css("h2 a").attrib.get("href", "")
            product_url = f"https://www.amazon.co.jp{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_jpy_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="amazon_jp",
                ))
        except Exception:
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        if not cleaned:
            return 0.0
        return round(float(cleaned) * 0.0067, 2)
    except ValueError:
        return 0.0
