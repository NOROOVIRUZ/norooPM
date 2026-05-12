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

HEADERS = {
    "Accept-Language": "ja-JP,ja;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    cat_id = CATEGORY_IDS.get(category, "")
    url = f"https://ranking.rakuten.co.jp/daily/{cat_id}/" if cat_id else \
          f"https://search.rakuten.co.jp/search/mall/{category}/?s=2"

    fetcher = Fetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, stealthy_headers=True)
    except Exception as e:
        print(f"[Rakuten] fetch 실패: {e}")
        return []

    products = []
    items = page.css(".rankingItem, .item, [class*='rankingItem']")

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css(".itemName, .title, [class*='itemName']")
            price_el = item.css(".price, [class*='price']")
            img_el = item.css("img")
            link_el = item.css("a")
            rank_el = item.css(".rank, [class*='rank']")

            rank_text = rank_el.get("").strip() if rank_el else str(i + 1)
            rank = int(rank_text) if rank_text.isdigit() else i + 1
            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _jpy_to_usd(price_str)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = href if href.startswith("http") else f"https://item.rakuten.co.jp{href}"

            if name:
                products.append(Product(
                    rank=rank, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="rakuten",
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.0, 2.0))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        cleaned = price_str.replace("¥", "").replace("円", "").replace(",", "").strip()
        return round(float(cleaned) * 0.0067, 2)
    except ValueError:
        return 0.0
