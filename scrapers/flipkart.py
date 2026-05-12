import time
import random
from scrapling.fetchers import Fetcher
from core.models import Product

HEADERS = {
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    url = f"https://www.flipkart.com/search?q={category}&otracker=search&sort=popularity"
    fetcher = Fetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, stealthy_headers=True)
    except Exception as e:
        print(f"[Flipkart] fetch 실패: {e}")
        return []

    products = []
    items = page.css("._1AtVbE, ._13oc-S, [data-id]")

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css("._4rR01T, .s1Q9rs, [class*='product-title']")
            price_el = item.css("._30jeq3, [class*='price']")
            img_el = item.css("img._396cs4, img[class*='product-image']")
            link_el = item.css("a[href*='/p/']")
            rating_el = item.css("._3LWZlK")
            reviews_el = item.css("._2_R_DZ span")

            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _inr_to_usd(price_str)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://www.flipkart.com{href}" if href.startswith("/") else href

            rating_str = rating_el.get("").strip() if rating_el else ""
            rating = float(rating_str) if rating_str else None
            reviews_str = reviews_el.get("").replace(",", "").replace("Ratings", "").strip() if reviews_el else ""
            reviews = int(reviews_str) if reviews_str.isdigit() else None

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="flipkart",
                    rating=rating, reviews=reviews,
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.0, 2.0))

    return products


def _inr_to_usd(price_str: str) -> float:
    try:
        cleaned = price_str.replace("₹", "").replace(",", "").strip()
        return round(float(cleaned) * 0.012, 2)
    except ValueError:
        return 0.0
