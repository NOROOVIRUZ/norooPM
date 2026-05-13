import re
import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    url = f"https://www.flipkart.com/search?q={category}&sort=popularity"
    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[Flipkart] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Flipkart] 실패: {e}")
        return []

    products = []
    # Flipkart search result containers — try multiple stable selectors
    items = page.css("[data-id], div[class*='_1AtVbE'], div[class*='_2kHMtA']")
    if not items:
        # Fallback: any anchor wrapping a product card
        items = page.css("div[class*='col'][class*='_2Kn22P'] > div")
    print(f"[Flipkart] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("a[title], div[class*='_4rR01T'], div[class*='KzDlHZ'], a[class*='s1Q9rs']").get("").strip()
            if not name:
                name = item.css("a").attrib.get("title", "").strip()
            price_str = item.css("div[class*='_30jeq3'], div[class*='Nx9bqj'], [class*='price']").get("").strip()
            thumbnail = item.css("img").attrib.get("src", "")
            href = item.css("a[href*='/p/'], a[href*='pid=']").attrib.get("href", "")
            if not href:
                href = item.css("a").attrib.get("href", "")
            product_url = f"https://www.flipkart.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_inr_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="flipkart",
                ))
        except Exception:
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _inr_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        if not cleaned:
            return 0.0
        return round(float(cleaned) * 0.012, 2)
    except ValueError:
        return 0.0
