import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

CATEGORY_NODES = {
    "전동칫솔": "4930254051",
    "마사지기": "4930255051",
    "이어폰": "2351652051",
    "블루투스스피커": "3210981",
    "공기청정기": "3538801",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    node_id = CATEGORY_NODES.get(category)
    if not node_id:
        return []

    url = f"https://www.amazon.co.jp/Best-Sellers/zgbs/hpc/{node_id}"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Amazon JP] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Amazon JP] 실패: {e}")
        return []

    products = []
    items = page.css("#zg-ordered-list .zg-item-immersion")
    print(f"[Amazon JP] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1, .p13n-sc-truncate-desktop-type2").get("").strip()
            price_str = item.css(".p13n-sc-price").get("").strip()
            thumbnail = item.css("img").attrib.get("src", "")
            href = item.css("a.a-link-normal").attrib.get("href", "")
            product_url = f"https://www.amazon.co.jp{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_jpy_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="amazon_jp",
                ))
        except Exception:
            continue
        time.sleep(random.uniform(0.5, 1.5))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        return round(float(price_str.replace("¥", "").replace(",", "").strip()) * 0.0067, 2)
    except ValueError:
        return 0.0
