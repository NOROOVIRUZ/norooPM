import { useState } from "react";
import { useManifest } from "./hooks/useManifest";
import { useProductData } from "./hooks/useProductData";
import ProductCard from "./components/ProductCard";
import { Product } from "./types";

const API = import.meta.env.VITE_API_URL ?? "";
const PLATFORMS = ["amazon", "amazon_jp", "aliexpress", "jd", "rakuten", "coupang", "shopee_tw", "shopee_sg", "flipkart"] as const;
type Platform = (typeof PLATFORMS)[number];

const PLATFORM_LABELS: Record<Platform, string> = {
  amazon: "Amazon US",
  amazon_jp: "Amazon JP",
  aliexpress: "AliExpress",
  jd: "JD.com",
  rakuten: "楽天",
  coupang: "쿠팡",
  shopee_tw: "Shopee TW",
  shopee_sg: "Shopee SG",
  flipkart: "Flipkart",
};

export default function App() {
  const { categories, manifest, loading: manifestLoading } = useManifest();
  const [selected, setSelected] = useState<string | null>(null);
  const [activePlatform, setActivePlatform] = useState<Platform>("amazon");
  const [query, setQuery] = useState("");
  const [triggering, setTriggering] = useState(false);
  const { data, loading, error } = useProductData(selected);

  const filtered = categories.filter((c) =>
    c.toLowerCase().includes(query.toLowerCase())
  );

  const products: Product[] = data?.platforms[activePlatform] ?? [];

  const lastUpdated = selected && manifest[selected]
    ? manifest[selected].last_updated
    : null;

  async function triggerScrape() {
    if (!selected) return;
    setTriggering(true);
    try {
      await fetch(`${API}/api/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ categories: selected }),
      });
      alert(`📡 "${selected}" 수집 요청됨!\n3~5분 후 Telegram 알림이 올 거야.`);
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>norooPM <span>시장조사 대시보드</span></h1>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <div className="search-wrap">
            <input
              type="text"
              placeholder="카테고리 검색..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          {manifestLoading ? (
            <p className="hint">로딩 중...</p>
          ) : (
            <ul className="category-list">
              {filtered.map((cat) => (
                <li
                  key={cat}
                  className={selected === cat ? "active" : ""}
                  onClick={() => { setSelected(cat); setActivePlatform("amazon"); }}
                >
                  {cat}
                  <span className="last-date">{manifest[cat]?.last_updated}</span>
                </li>
              ))}
              {filtered.length === 0 && (
                <li className="hint">카테고리 없음</li>
              )}
            </ul>
          )}
        </aside>

        <main className="content">
          {!selected ? (
            <div className="empty-state">
              <p>← 카테고리를 선택해줘</p>
            </div>
          ) : (
            <>
              <div className="content-header">
                <div>
                  <h2>{selected}</h2>
                  {lastUpdated && (
                    <span className="last-updated">마지막 수집: {lastUpdated}</span>
                  )}
                </div>
                <button
                  className="trigger-btn"
                  onClick={triggerScrape}
                  disabled={triggering}
                >
                  {triggering ? "요청 중..." : "🔄 지금 수집"}
                </button>
              </div>

              <div className="platform-tabs">
                {PLATFORMS.map((p) => (
                  <button
                    key={p}
                    className={activePlatform === p ? "active" : ""}
                    onClick={() => setActivePlatform(p)}
                  >
                    {PLATFORM_LABELS[p]}
                    {data?.platforms[p] && (
                      <span className="count">{data.platforms[p]!.length}</span>
                    )}
                  </button>
                ))}
              </div>

              {loading && <p className="hint">수집 데이터 로딩 중...</p>}
              {error && (
                <div className="error-state">
                  <p>아직 수집된 데이터가 없어.</p>
                  <button onClick={triggerScrape} disabled={triggering}>
                    지금 수집 요청하기
                  </button>
                </div>
              )}
              {!loading && !error && products.length === 0 && (
                <p className="hint">이 플랫폼 데이터 없음</p>
              )}
              <div className="product-grid">
                {products.map((p) => (
                  <ProductCard key={`${p.platform}-${p.rank}`} product={p} />
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
