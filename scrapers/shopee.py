import time
import random
from scrapling.fetchers import StealthyFetcher
from core.models import Product

# Shopee 국가별 도메인
COUNTRY_DOMAINS = {
    "tw": "shopee.tw",
    "sg": "shopee.sg",
}

HEADERS_MAP = {
    "tw": {"Accept-Language": "zh-TW,zh;q=0.9"},
    "sg": {"Accept-Language": "en-SG,en;q=0.9"},
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    products = []
    for country, domain in COUNTRY_DOMAINS.items():
        result = _scrape_country(category, domain, country, max_items)
        products.extend(result)
    return products


def _scrape_country(category: str, domain: str, country: str, max_items: int) -> list[Product]:
    url = f"https://{domain}/search?keyword={category}&sortBy=sales&page=0"
    fetcher = StealthyFetcher(auto_match=False)

    try:
        page = fetcher.get(
            url, headers=HEADERS_MAP[country],
            headless=True, network_idle=True,
        )
    except Exception as e:
        print(f"[Shopee {country.upper()}] fetch 실패: {e}")
        return []

    items = page.css("[data-sqe='item'], .shopee-search-item-result__item")
    result = []

    for i, item in enumerate(items[:max_items]):
        try:
            name_el = item.css("[class*='name'], [class*='title']")
            price_el = item.css("[class*='price']")
            img_el = item.css("img")
            link_el = item.css("a")

            name = name_el.get("").strip() if name_el else ""
            price_str = price_el.get("").strip() if price_el else ""
            price_usd = _local_to_usd(price_str, country)
            thumbnail = img_el.attrib.get("src", "") if img_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            product_url = f"https://{domain}{href}" if href.startswith("/") else href

            if name:
                result.append(Product(
                    rank=i + 1, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url,
                    platform=f"shopee_{country}",
                ))
        except Exception:
            continue

        time.sleep(random.uniform(1.5, 2.5))

    return result


def _local_to_usd(price_str: str, country: str) -> float:
    rates = {"tw": 0.031, "sg": 0.74}
    try:
        cleaned = price_str.replace("$", "").replace("NT$", "").replace(",", "").strip()
        if "~" in cleaned:
            cleaned = cleaned.split("~")[0].strip()
        return round(float(cleaned) * rates.get(country, 1.0), 2)
    except ValueError:
        return 0.0
