import re
import time
import random
from scrapling.fetchers import StealthyFetcher
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
    if cat_id:
        url = f"https://ranking.rakuten.co.jp/daily/{cat_id}/"
    else:
        url = f"https://search.rakuten.co.jp/search/mall/{category}/?s=2"

    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[Rakuten] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Rakuten] 실패: {e}")
        return []

    products = []
    items = page.css(".rnkgItem, .rankingItem, [class*='rnkgItem']")
    if not items:
        items = page.css(".searchresultitem, [class*='item--']")
    print(f"[Rakuten] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name_els = item.css(".rnkgItemName a, .itemName a, h2 a, [class*='itemName'] a")
            name = name_els.get("").strip()

            price_els = item.css(".price, [class*='price--']")
            price_str = price_els.get("").strip() if price_els else ""

            img_els = item.css("img")
            thumbnail = img_els.attrib.get("src", "") if img_els else ""

            link_els = item.css(".rnkgItemName a") or item.css("a[href*='item.rakuten']") or item.css("a")
            href = link_els.attrib.get("href", "") if link_els else ""
            product_url = href if href.startswith("http") else f"https://search.rakuten.co.jp{href}"

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_jpy_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="rakuten",
                ))
        except Exception as e:
            print(f"[Rakuten] 아이템 {i} 파싱 오류: {e}")
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        if not cleaned:
            return 0.0
        return round(float(cleaned) * 0.0067, 2)
    except ValueError:
        return 0.0
