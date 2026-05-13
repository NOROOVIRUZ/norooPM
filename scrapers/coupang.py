import re
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


def scrape(category: str, max_items: int = 20) -> list[Product]:
    cat_id = CATEGORY_IDS.get(category)
    url = (f"https://www.coupang.com/np/categories/{cat_id}?listSize=36&sorter=bestRank" if cat_id
           else f"https://www.coupang.com/np/search?q={category}&sorter=bestRank")

    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[Coupang] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Coupang] 실패: {e}")
        return []

    products = []
    items = page.css("li.baby-product, .search-product")
    print(f"[Coupang] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css(".name, .product-name").get("").strip()
            price_val = item.css(".price-value").get("").strip()
            price_str = f"₩{price_val}" if price_val else ""

            src = (item.css("img::attr(src)").get("")
                   or item.css("img::attr(data-img-src)").get(""))
            thumbnail = f"https:{src}" if src.startswith("//") else src

            href = (item.css("a[href*='/vp/products/']::attr(href)").get("")
                    or item.css("a::attr(href)").get(""))
            product_url = f"https://www.coupang.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_krw_to_usd(price_val),
                    thumbnail=thumbnail, product_url=product_url, platform="coupang",
                ))
        except Exception as e:
            print(f"[Coupang] 아이템 {i} 오류: {e}")
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _krw_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return round(float(cleaned) * 0.00073, 2) if cleaned else 0.0
    except ValueError:
        return 0.0
