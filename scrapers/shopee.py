import re
import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product

COUNTRIES = {
    "tw": ("shopee.tw", 0.031),
    "sg": ("shopee.sg", 0.74),
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    products = []
    for country, (domain, rate) in COUNTRIES.items():
        products.extend(_scrape_country(category, domain, country, rate, max_items))
    return products


def _scrape_country(category, domain, country, rate, max_items):
    url = f"https://{domain}/search?keyword={category}&sortBy=sales"
    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[Shopee {country.upper()}] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Shopee {country.upper()}] 실패: {e}")
        return []

    items = page.css("[data-sqe='item'], .shopee-search-item-result__item")
    print(f"[Shopee {country.upper()}] 아이템 수: {len(items)}")
    result = []

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("[class*='name']::text, [class*='title']::text").get("").strip()
            price_str = item.css("[class*='price']::text").get("").strip()
            thumbnail = item.css("img::attr(src)").get("")
            href = item.css("a::attr(href)").get("")
            product_url = f"https://{domain}{href}" if href.startswith("/") else href

            if name:
                result.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_to_usd(price_str, rate),
                    thumbnail=thumbnail, product_url=product_url,
                    platform=f"shopee_{country}",
                ))
        except Exception as e:
            print(f"[Shopee {country.upper()}] 아이템 {i} 오류: {e}")
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return result


def _to_usd(price_str: str, rate: float) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str.split("~")[0])
        return round(float(cleaned) * rate, 2) if cleaned else 0.0
    except ValueError:
        return 0.0
