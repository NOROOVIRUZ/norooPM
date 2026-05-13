import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

CATEGORY_IDS = {
    "전동칫솔": "100227",
    "마사지기": "100316",
    "이어폰": "100019",
    "블루투스스피커": "100019",
    "공기청정기": "100804",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    cat_id = CATEGORY_IDS.get(category, "")
    url = (f"https://ranking.rakuten.co.jp/daily/{cat_id}/" if cat_id
           else f"https://search.rakuten.co.jp/search/mall/{category}/?s=2")

    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Rakuten] 상태:{page.status}")
    except Exception as e:
        print(f"[Rakuten] 실패: {e}")
        return []

    products = []
    items = page.css(".rankingItem, .item, [class*='rankingItem']")
    print(f"[Rakuten] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css(".itemName, [class*='itemName']").get("").strip()
            price_str = item.css(".price, [class*='price']").get("").strip()
            thumbnail = item.css("img").attrib.get("src", "")
            href = item.css("a").attrib.get("href", "")
            product_url = href if href.startswith("http") else f"https://item.rakuten.co.jp{href}"

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_jpy_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="rakuten",
                ))
        except Exception:
            continue
        time.sleep(random.uniform(0.5, 1.5))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        return round(float(price_str.replace("¥", "").replace("円", "").replace(",", "").strip()) * 0.0067, 2)
    except ValueError:
        return 0.0
