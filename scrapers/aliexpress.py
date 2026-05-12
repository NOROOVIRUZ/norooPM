import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    query = category
    url = f"https://www.aliexpress.com/wholesale?SearchText={query}&SortType=best_match&page=1"

    fetcher = StealthyFetcher(auto_match=False)

    try:
        page = fetcher.get(url, headless=True, network_idle=True)
    except Exception as e:
        print(f"[AliExpress] fetch 실패: {e}")
        return []

    products = []
    items = page.css(".search-item-card-wrapper-gallery, [class*='product-snippet']")

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css("h3, [class*='title'], [class*='product-title']")
            price_el = item.css("[class*='price--current'], [class*='sale-price']")
            img_el = item.css("img")
            link_el = item.css("a")
            rating_el = item.css("[class*='rating'], [class*='star']")
            sales_el = item.css("[class*='sold'], [class*='trade']")

            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _parse_price(price_str)
            thumbnail = img_el.attrib.get("src", "") or img_el.attrib.get("data-src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https:{href}" if href.startswith("//") else href
            sales = sales_el.get("").strip() if sales_el else None

            if name:
                products.append(Product(
                    rank=i + 1,
                    name=name,
                    price=price_str,
                    price_usd=price_usd,
                    thumbnail=thumbnail,
                    product_url=product_url,
                    platform="aliexpress",
                    sales=sales,
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.5, 3.0))

    return products


def _parse_price(price_str: str) -> float:
    try:
        cleaned = price_str.replace("US $", "").replace("$", "").replace(",", "").strip()
        if "–" in cleaned or "-" in cleaned:
            cleaned = cleaned.split("–")[0].split("-")[0].strip()
        return float(cleaned)
    except ValueError:
        return 0.0
