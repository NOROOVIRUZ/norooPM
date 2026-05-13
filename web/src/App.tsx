import { useState } from "react";
import { useManifest } from "./hooks/useManifest";
import { useProductData } from "./hooks/useProductData";
import ProductCard from "./components/ProductCard";
import { Product } from "./types";

const API = import.meta.env.VITE_API_URL ?? "";
const SHEETS_URL = import.meta.env.VITE_SHEETS_URL ?? "";

const PLATFORMS = ["naver", "amazon_jp"] as const;
type Platform = (typeof PLATFORMS)[number];

const PLATFORM_LABELS: Record<Platform, string> = {
  naver: "네이버쇼핑",
  amazon_jp: "Amazon JP",
};

async function logToSheets(category: string, platform: string, products: Product[]) {
  if (!SHEETS_URL || products.length === 0) return;
  const now = new Date().toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });
  try {
    await fetch(SHEETS_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        timestamp: now,
        category,
        platform,
        count: products.length,
        top5: products.slice(0, 5).map((p) => ({
          rank: p.rank,
          name: p.name,
          price: p.price,
          url: p.product_url,
        })),
      }),
    });
  } catch {
    // no-cors 방식이라 에러 무시
  }
}

export default function App() {
  const { categories, manifest, loading: manifestLoading } = useManifest();
  const [selected, setSelected] = useState<string | null>(null);
  const [activePlatform, setActivePlatform] = useState<Platform>("naver");
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

  function handlePlatformChange(p: Platform) {
    setActivePlatform(p);
    if (selected && data?.platforms[p]?.length) {
      logToSheets(selected, p, data.platforms[p]!);
    }
  }

  function handleCategorySelect(cat: string) {
    setSelected(cat);
    setActivePlatform("naver");
  }

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
        <div className="header-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="15" stroke="#e63946" strokeWidth="2"/>
            <circle cx="16" cy="16" r="10" stroke="#e63946" strokeWidth="1.5" strokeDasharray="3 2"/>
            <circle cx="16" cy="16" r="5" stroke="#e63946" strokeWidth="1.5"/>
            <circle cx="16" cy="16" r="2" fill="#e63946"/>
            <line x1="16" y1="1" x2="16" y2="6" stroke="#e63946" strokeWidth="2"/>
            <line x1="31" y1="16" x2="26" y2="16" stroke="#e63946" strokeWidth="2"/>
          </svg>
        </div>
        <div className="header-title">
          <span className="title-main">noroo_Bot_asuka</span>
          <span className="title-sub">sourcing</span>
        </div>
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
                  onClick={() => handleCategorySelect(cat)}
                >
                  <span>{cat}</span>
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
              <svg width="48" height="48" viewBox="0 0 32 32" fill="none" opacity="0.3">
                <circle cx="16" cy="16" r="15" stroke="#e63946" strokeWidth="2"/>
                <circle cx="16" cy="16" r="10" stroke="#e63946" strokeWidth="1.5" strokeDasharray="3 2"/>
                <circle cx="16" cy="16" r="5" stroke="#e63946" strokeWidth="1.5"/>
                <circle cx="16" cy="16" r="2" fill="#e63946"/>
              </svg>
              <p>카테고리를 선택해줘</p>
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
                <button className="trigger-btn" onClick={triggerScrape} disabled={triggering}>
                  {triggering ? "요청 중..." : "🔄 지금 수집"}
                </button>
              </div>

              <div className="platform-tabs">
                {PLATFORMS.map((p) => (
                  <button
                    key={p}
                    className={activePlatform === p ? "active" : ""}
                    onClick={() => handlePlatformChange(p)}
                  >
                    {PLATFORM_LABELS[p]}
                    {data?.platforms[p]?.length ? (
                      <span className="count">{data.platforms[p]!.length}</span>
                    ) : null}
                  </button>
                ))}
              </div>

              {loading && <p className="hint">데이터 로딩 중...</p>}
              {error && (
                <div className="error-state">
                  <p>아직 수집된 데이터가 없어.</p>
                  <button onClick={triggerScrape} disabled={triggering}>지금 수집 요청하기</button>
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
