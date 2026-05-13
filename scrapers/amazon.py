import re
import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product

CATEGORY_NODES = {
    "전동칫솔": "1232614011",
    "마사지기": "3760911",
    "이어폰": "2102313011",
    "블루투스스피커": "2975312011",
    "공기청정기": "2102148011",
    "안마기": "3760911",
    "드라이어": "11036781",
    "로봇청소기": "2492080011",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    node_id = CATEGORY_NODES.get(category)
    url = (f"https://www.amazon.com/Best-Sellers/zgbs/hpc/{node_id}" if node_id
           else f"https://www.amazon.com/s?k={category}&s=exact-aware-popularity-rank")

    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True, disable_resources=True)
        print(f"[Amazon] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Amazon] 실패: {e}")
        return []

    items = page.css("#zg-ordered-list .zg-item-immersion")
    if not items:
        items = page.css("[data-component-type='s-search-result']")
    print(f"[Amazon] 아이템 수: {len(items)}")

    products = []
    for i, item in enumerate(items[:max_items]):
        try:
            name = (item.css("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1").get("")
                    or item.css("h2 span").get("")).strip()
            price_str = (item.css(".p13n-sc-price").get("")
                         or item.css(".a-price .a-offscreen").get("")).strip()
            thumbnail = (item.css("img::attr(src)").get(""))
            href = (item.css("a.a-link-normal::attr(href)").get("")
                    or item.css("h2 a::attr(href)").get(""))
            product_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_parse_price(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="amazon",
                ))
        except Exception as e:
            print(f"[Amazon] 아이템 {i} 오류: {e}")
            continue

    return products


def _parse_price(s: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', s)
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0
