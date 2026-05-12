import time
import random
from typing import Optional
from scrapling.fetchers import Fetcher
from core.models import Product

# Amazon Best Sellers category slug 매핑
CATEGORY_SLUGS = {
    "전동칫솔": "health-personal-care/zgbs/hpc/7698256011",
    "마사지기": "health-personal-care/zgbs/hpc/3764231",
    "이어폰": "electronics/zgbs/electronics/172282",
    "블루투스스피커": "electronics/zgbs/electronics/2811119011",
    "공기청정기": "home/zgbs/home/2619526011",
}

BASE_URL = "https://www.amazon.com/Best-Sellers"
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    slug = CATEGORY_SLUGS.get(category)
    if not slug:
        slug = f"zgbs?search={category}"

    url = f"{BASE_URL}/{slug}"
    fetcher = Fetcher(auto_match=False)

    try:
        page = fetcher.get(url, headers=HEADERS, stealthy_headers=True)
    except Exception as e:
        print(f"[Amazon] fetch 실패: {e}")
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
            rating_el = item.css(".a-icon-star-small .a-icon-alt, .a-icon-star .a-icon-alt")
            reviews_el = item.css(".a-size-small .a-link-normal")

            rank_text = rank_el.get("") if rank_el else ""
            rank = int(rank_text.replace("#", "").replace(",", "").strip()) if rank_text else len(products) + 1

            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _parse_price(price_str)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            rating_str = rating_el.get("") if rating_el else ""
            rating = float(rating_str.split(" ")[0]) if rating_str else None

            reviews_str = reviews_el.get("").replace(",", "") if reviews_el else ""
            reviews = int(reviews_str) if reviews_str.isdigit() else None

            if name:
                products.append(Product(
                    rank=rank,
                    name=name,
                    price=price_str,
                    price_usd=price_usd,
                    thumbnail=thumbnail,
                    product_url=product_url,
                    platform="amazon",
                    rating=rating,
                    reviews=reviews,
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.0, 2.5))

    return products


def _parse_price(price_str: str) -> float:
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0
