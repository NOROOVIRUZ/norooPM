import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    url = f"https://www.aliexpress.com/wholesale?SearchText={category}&SortType=best_match"
    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[AliExpress] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[AliExpress] 실패: {e}")
        return []

    products = []
    items = page.css(".search-item-card-wrapper-gallery, [class*='product-snippet']")
    print(f"[AliExpress] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("h3, [class*='title']").get("").strip()
            price_str = item.css("[class*='price--current'], [class*='sale-price']").get("").strip()
            src = item.css("img").attrib.get("src", "") or item.css("img").attrib.get("data-src", "")
            thumbnail = f"https:{src}" if src.startswith("//") else src
            href = item.css("a").attrib.get("href", "")
            product_url = f"https:{href}" if href.startswith("//") else href
            sales = item.css("[class*='sold'], [class*='trade']").get("").strip() or None

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_parse_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url,
                    platform="aliexpress", sales=sales,
                ))
        except Exception:
            continue
        time.sleep(random.uniform(1.0, 2.0))

    return products


def _parse_usd(price_str: str) -> float:
    try:
        cleaned = price_str.replace("US $", "").replace("$", "").replace(",", "").strip()
        if "–" in cleaned:
            cleaned = cleaned.split("–")[0].strip()
        return float(cleaned)
    except ValueError:
        return 0.0
