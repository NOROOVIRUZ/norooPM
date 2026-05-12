import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product

CATEGORY_IDS = {
    "전동칫솔": "187101",
    "마사지기": "186966",
    "이어폰": "186966",
    "블루투스스피커": "186966",
    "공기청정기": "186966",
}

HEADERS = {
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    cat_id = CATEGORY_IDS.get(category, "")
    if cat_id:
        url = f"https://www.coupang.com/np/categories/{cat_id}?listSize=36&rating=0&isPrimeOnly=0&sorter=bestRank"
    else:
        url = f"https://www.coupang.com/np/search?q={category}&channel=user&isPrimeOnly=0&sorter=bestRank"

    fetcher = StealthyFetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, headless=True, network_idle=True)
    except Exception as e:
        print(f"[Coupang] fetch 실패: {e}")
        return []

    products = []
    items = page.css("li.baby-product, .search-product")

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css(".name, .product-name, [class*='name']")
            price_el = item.css(".price-value, [class*='price-value']")
            img_el = item.css("img.search-product-wrap-img, img[class*='product-img']")
            link_el = item.css("a[href*='/vp/products/']")

            name = name_el.get("").strip() if name_el else ""
            price_str = f"₩{price_el.get('').strip()}" if price_el else ""
            price_usd = _krw_to_usd(price_el.get("").strip() if price_el else "0")
            src = img_el.attrib.get("src", "") or img_el.attrib.get("data-img-src", "") if img_el else ""
            thumbnail = f"https:{src}" if src.startswith("//") else src
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://www.coupang.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="coupang",
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.5, 3.0))

    return products


def _krw_to_usd(price_str: str) -> float:
    try:
        cleaned = price_str.replace(",", "").strip()
        return round(float(cleaned) * 0.00073, 2)
    except ValueError:
        return 0.0
