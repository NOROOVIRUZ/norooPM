import re
import os
import httpx
from core.models import Product


def scrape(category: str, max_items: int = 20) -> list[Product]:
    client_id = os.environ.get("NAVER_CLIENT_ID", "")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("[Naver] API 키 없음 — NAVER_CLIENT_ID/SECRET 환경변수 확인")
        return []

    try:
        resp = httpx.get(
            "https://openapi.naver.com/v1/search/shop.json",
            params={"query": category, "display": max_items, "sort": "sim"},
            headers={
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret,
            },
            timeout=15,
        )
        print(f"[Naver] 상태:{resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Naver] 실패: {e}")
        return []

    items = data.get("items", [])
    print(f"[Naver] 아이템 수: {len(items)}")

    products = []
    for i, item in enumerate(items[:max_items]):
        try:
            name = re.sub(r'<[^>]+>', '', item.get("title", "")).strip()
            price_val = item.get("lprice", "")
            price_str = f"₩{int(price_val):,}" if price_val else ""
            mall = item.get("mallName", "")

            if name:
                products.append(Product(
                    rank=i + 1,
                    name=name,
                    price=price_str,
                    price_usd=_krw_to_usd(price_val),
                    thumbnail=item.get("image", ""),
                    product_url=item.get("link", ""),
                    platform=f"naver_{mall}" if mall else "naver",
                ))
        except Exception as e:
            print(f"[Naver] 아이템 {i} 오류: {e}")
            continue

    return products


def _krw_to_usd(price_str: str) -> float:
    try:
        return round(float(price_str.replace(",", "")) * 0.00073, 2)
    except ValueError:
        return 0.0
