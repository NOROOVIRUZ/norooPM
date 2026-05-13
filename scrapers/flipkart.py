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
    items = page.css("[data-id]")
    if not items:
        items = page.css("div[class*='_1AtVbE']")
    print(f"[Flipkart] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = (item.css("a::attr(title)").get("")
                    or item.css("div[class*='KzDlHZ']").get("")
                    or item.css("div[class*='_4rR01T']").get("")).strip()
            price_str = (item.css("div[class*='Nx9bqj']").get("")
                         or item.css("div[class*='_30jeq3']").get("")).strip()
            thumbnail = item.css("img::attr(src)").get("")
            href = (item.css("a[href*='/p/']::attr(href)").get("")
                    or item.css("a[href*='pid=']::attr(href)").get("")
                    or item.css("a::attr(href)").get(""))
            product_url = f"https://www.flipkart.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_inr_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="flipkart",
                ))
        except Exception as e:
            print(f"[Flipkart] 아이템 {i} 오류: {e}")
            continue
        time.sleep(random.uniform(0.3, 0.8))

    return products


def _inr_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return round(float(cleaned) * 0.012, 2) if cleaned else 0.0
    except ValueError:
        return 0.0
