import time
import random
import xml.etree.ElementTree as ET
from scrapling.fetchers import Fetcher
from core.models import Product

# Amazon Best Sellers RSS 피드 (IP 차단 없음)
# nodeId: https://www.amazon.com/Best-Sellers 에서 카테고리 선택 후 URL에서 확인
CATEGORY_NODES = {
    "전동칫솔": "1232614011",   # Electric Toothbrushes
    "마사지기": "3760911",       # Massagers
    "이어폰": "2102313011",      # Earbud Headphones
    "블루투스스피커": "2975312011", # Portable Bluetooth Speakers
    "공기청정기": "2102148011",  # Air Purifiers
    "안마기": "3760911",
    "드라이어": "11036781",      # Hair Dryers
    "로봇청소기": "2492080011",  # Robotic Vacuums
}

RSS_BASE = "https://www.amazon.com/rss/bestsellers"
HEADERS = {
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (compatible; RSS reader)",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    node_id = CATEGORY_NODES.get(category)
    if not node_id:
        print(f"[Amazon] '{category}' nodeId 없음 — 검색 방식으로 폴백")
        return _scrape_search(category, max_items)

    url = f"{RSS_BASE}/hpc/{node_id}?pg=1&tag=noroo-20&rss=1"
    fetcher = Fetcher(auto_match=False)

    try:
        resp = fetcher.get(url, headers=HEADERS, stealthy_headers=False)
        print(f"[Amazon RSS] 상태: {resp.status} / 길이: {len(resp.html_content)}")
    except Exception as e:
        print(f"[Amazon RSS] fetch 실패: {e} — 검색 폴백")
        return _scrape_search(category, max_items)

    products = _parse_rss(resp.html_content, max_items)
    if not products:
        print("[Amazon RSS] 파싱 결과 없음 — 검색 폴백")
        return _scrape_search(category, max_items)

    return products


def _parse_rss(xml_text: str, max_items: int) -> list[Product]:
    products = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        items = root.findall(".//item")

        for i, item in enumerate(items[:max_items]):
            try:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                desc = item.findtext("description", "")

                # 가격 파싱 (description 안에 있음)
                price_str = ""
                price_usd = 0.0
                if "$" in desc:
                    import re
                    m = re.search(r'\$[\d,]+\.?\d*', desc)
                    if m:
                        price_str = m.group()
                        price_usd = float(price_str.replace("$", "").replace(",", ""))

                # 썸네일 파싱
                thumbnail = ""
                if "img" in desc.lower():
                    import re
                    m = re.search(r'src=["\']([^"\']+)["\']', desc)
                    if m:
                        thumbnail = m.group(1)

                if title:
                    products.append(Product(
                        rank=i + 1,
                        name=title,
                        price=price_str,
                        price_usd=price_usd,
                        thumbnail=thumbnail,
                        product_url=link,
                        platform="amazon",
                    ))
            except Exception:
                continue
    except ET.ParseError as e:
        print(f"[Amazon RSS] XML 파싱 실패: {e}")

    return products


def _scrape_search(category: str, max_items: int) -> list[Product]:
    """RSS 실패 시 폴백: 검색 결과 페이지"""
    from scrapling.fetchers import StealthyFetcher

    CATEGORY_EN = {
        "전동칫솔": "electric+toothbrush",
        "마사지기": "body+massager",
        "이어폰": "wireless+earbuds",
        "블루투스스피커": "bluetooth+speaker",
        "공기청정기": "air+purifier",
    }
    keyword = CATEGORY_EN.get(category, category)
    url = f"https://www.amazon.com/s?k={keyword}&s=exact-aware-popularity-rank"

    fetcher = StealthyFetcher(auto_match=False)
    try:
        page = fetcher.get(url, headless=True, network_idle=True, disable_resources=True)
    except Exception as e:
        print(f"[Amazon Search] fetch 실패: {e}")
        return []

    products = []
    items = page.css("[data-component-type='s-search-result']")
    print(f"[Amazon Search] 아이템 수: {len(items)}")

    for i, item in enumerate(items[:max_items]):
        try:
            name = item.css("h2 a span").get("").strip()
            price_str = item.css(".a-price .a-offscreen").get("").strip()
            price_usd = _parse_price(price_str)
            thumbnail = item.css("img.s-image").attrib.get("src", "")
            href = item.css("h2 a.a-link-normal").attrib.get("href", "")
            product_url = f"https://www.amazon.com{href}" if href.startswith("/") else href

            if name:
                products.append(Product(
                    rank=i + 1, name=name, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=product_url, platform="amazon",
                ))
        except Exception:
            continue

    return products


def _parse_price(price_str: str) -> float:
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0
