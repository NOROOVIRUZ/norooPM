import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    url = f"https://www.flipkart.com/search?q={category}&sort=popularity"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Flipkart] 상태:{page.status}")
    except Exception as e:
        print(f"[Flipkart] 실패: {e}")
        return []

    products = []
    items = page.css("._1AtVbE, ._13oc-S")
    print(f"[Flipkart] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("._4rR01T, .s1Q9rs").get("").strip()
            price_str = item.css("._30jeq3").get("").strip()
            thumbnail = item.css("img._396cs4").attrib.get("src", "")
            href = item.css("a[href*='/p/']").attrib.get("href", "")
            product_url = f"https://www.flipkart.com{href}" if href.startswith("/") else href
            rating_str = item.css("._3LWZlK").get("").strip()
            rating = float(rating_str) if rating_str else None

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str,
                    price_usd=_inr_to_usd(price_str),
                    thumbnail=thumbnail, product_url=product_url,
                    platform="flipkart", rating=rating,
                ))
        except Exception:
            continue
        time.sleep(random.uniform(0.5, 1.5))

    return products


def _inr_to_usd(price_str: str) -> float:
    try:
        return round(float(price_str.replace("₹", "").replace(",", "").strip()) * 0.012, 2)
    except ValueError:
        return 0.0
