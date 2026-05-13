import re
import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product

CATEGORY_EN = {
    "전동칫솔": "electric toothbrush",
    "마사지기": "massage gun",
    "이어폰": "earphones",
    "블루투스스피커": "bluetooth speaker",
    "공기청정기": "air purifier",
    "안마기": "massager",
    "드라이어": "hair dryer",
    "로봇청소기": "robot vacuum",
}

# SGD → USD (1 SGD ≈ 0.74 USD)
SGD_TO_USD = 0.74


def scrape(category: str, max_items: int = 20) -> list[Product]:
    query = CATEGORY_EN.get(category, category)
    url = f"https://www.lazada.sg/catalog/?q={query}&sort=popularity"

    try:
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        print(f"[Lazada] 상태:{page.status} 길이:{len(page.html_content)}")
    except Exception as e:
        print(f"[Lazada] 실패: {e}")
        return []

    products = []
    # Lazada 상품 카드 셀렉터 (여러 버전 대응)
    items = page.css("[data-qa-locator='product-item']")
    if not items:
        items = page.css("[class*='gridItem--']")
    if not items:
        items = page.css("div[class*='Bm3ON']")
    print(f"[Lazada] 아이템 수: {len(items)}")

    # 디버그: 첫 아이템 구조 파악
    if items:
        first = items[0]
        print(f"[Lazada DEBUG] title attr: {first.css('a::attr(title)').get('')!r}")
        print(f"[Lazada DEBUG] a::text: {first.css('a::text').get('')!r}")
        print(f"[Lazada DEBUG] img src: {first.css('img::attr(src)').get('')!r}")
        print(f"[Lazada DEBUG] price text: {first.css('[class*=price]::text').get('')!r}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = (item.css("a::attr(title)").get("")
                    or item.css("[class*='title']::text").get("")
                    or item.css("a::text").get("")).strip()
            price_str = (item.css("[class*='price']::text").get("")
                         or item.css("[class*='Price']::text").get("")).strip()
            thumbnail = (item.css("img::attr(src)").get("")
                         or item.css("img::attr(data-src)").get(""))
            href = item.css("a::attr(href)").get("")
            product_url = f"https://www.lazada.sg{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_sgd_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url, platform="lazada",
                ))
        except Exception as e:
            print(f"[Lazada] 아이템 {i} 오류: {e}")
            continue
        time.sleep(random.uniform(0.5, 1.0))

    return products


def _sgd_to_usd(price_str: str) -> float:
    try:
        cleaned = re.sub(r'[^\d.]', '', price_str)
        return round(float(cleaned) * SGD_TO_USD, 2) if cleaned else 0.0
    except ValueError:
        return 0.0
