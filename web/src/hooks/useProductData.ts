import { useEffect, useState } from "react";
import { ScrapeResult } from "../types";

const API = import.meta.env.VITE_API_URL ?? "";

export function useProductData(category: string | null) {
  const [data, setData] = useState<ScrapeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!category) return;
    setLoading(true);
    setError(null);

    fetch(`${API}/api/data/${encodeURIComponent(category)}`)
      .then((r) => {
        if (!r.ok) throw new Error("데이터 없음");
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [category]);

  return { data, loading, error };
}
