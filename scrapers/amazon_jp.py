import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

CATEGORY_SLUGS = {
    "전동칫솔": "hpc/zgbs/hpc/2151981051",
    "마사지기": "hpc/zgbs/hpc/2151998051",
    "이어폰": "electronics/zgbs/electronics/2151981051",
    "블루투스스피커": "electronics/zgbs/electronics/3210981",
    "공기청정기": "home/zgbs/home/2151981051",
}

BASE_URL = "https://www.amazon.co.jp/Best-Sellers"
HEADERS = {
    "Accept-Language": "ja-JP,ja;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    slug = CATEGORY_SLUGS.get(category, f"zgbs?search={category}")
    url = f"{BASE_URL}/{slug}"
    fetcher = Fetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, stealthy_headers=True)
    except Exception as e:
        print(f"[Amazon JP] fetch 실패: {e}")
        return []

    products = []
    items = page.css("#zg-ordered-list .zg-item-immersion")

    for item in items[:max_items]:
        try:
            rank_el = item.css(".zg-bdg-text")
            name_el = item.css("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1, .p13n-sc-truncate-desktop-type2")
            price_el = item.css(".p13n-sc-price")
            img_el = item.css("img.a-dynamic-image, img.p13n-product-image")
            link_el = item.css("a.a-link-normal")

            rank_text = rank_el.get("").replace("#", "").replace(",", "").strip()
            rank = int(rank_text) if rank_text.isdigit() else len(products) + 1
            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _jpy_to_usd(price_str)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://www.amazon.co.jp{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=rank, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="amazon_jp",
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.0, 2.5))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        cleaned = price_str.replace("¥", "").replace(",", "").strip()
        return round(float(cleaned) * 0.0067, 2)
    except ValueError:
        return 0.0
