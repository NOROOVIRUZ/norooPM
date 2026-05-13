import re
import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

CATEGORY_JP = {
    "전동칫솔": "電動歯ブラシ",
    "마사지기": "マッサージガン",
    "이어폰": "イヤホン",
    "블루투스스피커": "Bluetoothスピーカー",
    "공기청정기": "空気清浄機",
    "안마기": "マッサージ機",
    "드라이어": "ヘアドライヤー",
    "로봇청소기": "ロボット掃除機",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    query = CATEGORY_JP.get(category, category)
    url = f"https://www.amazon.co.jp/s?k={query}&s=relevanceblender"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Amazon JP] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Amazon JP] 실패: {e}")
        return []

    products = []
    items = page.css("[data-component-type='s-search-result']")
    print(f"[Amazon JP] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = (item.css("h2 span::text").get("")
                    or item.css("h2 a::text").get("")).strip()
            price_str = item.css(".a-price .a-offscreen::text").get("").strip()
            thumbnail = (item.css("img.s-image::attr(src)").get("")
                         or item.css("img::attr(src)").get(""))
            href = (item.css("a[href*='/dp/']::attr(href)").get("")
                    or item.css("a.a-link-normal::attr(href)").get(""))
            product_url = f"https://www.amazon.co.jp{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_jpy_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="amazon_jp",
                ))
        except Exception as e:
            print(f"[Amazon JP] 아이템 {i} 오류: {e}")
            continue
        time.sleep(random.uniform(0.3, 0.8))

    return products


def _jpy_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return round(float(cleaned) * 0.0067, 2) if cleaned else 0.0
    except ValueError:
        return 0.0
