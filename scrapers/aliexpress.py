import re
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
            price_els = item.css("[class*='price--current'], [class*='sale-price']")
            price_str = price_els.get("").strip() if price_els else ""

            img_els = item.css("img")
            if img_els:
                src = img_els.attrib.get("src", "") or img_els.attrib.get("data-src", "")
                thumbnail = f"https:{src}" if src.startswith("//") else src
            else:
                thumbnail = ""

            link_els = item.css("a")
            href = link_els.attrib.get("href", "") if link_els else ""
            product_url = f"https:{href}" if href.startswith("//") else href

            sales_els = item.css("[class*='sold'], [class*='trade']")
            sales = sales_els.get("").strip() or None if sales_els else None

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_parse_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url,
                    platform="aliexpress", sales=sales,
                ))
        except Exception as e:
            print(f"[AliExpress] 아이템 {i} 파싱 오류: {e}")
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _parse_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        if not cleaned:
            return 0.0
        parts = cleaned.split('.')
        if len(parts) > 2:
            cleaned = '.'.join([parts[0], parts[-1]])
        return float(cleaned)
    except ValueError:
        return 0.0
