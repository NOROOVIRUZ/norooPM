import { useEffect, useState } from "react";
import { Manifest } from "../types";

const API = import.meta.env.VITE_API_URL ?? "";

export function useManifest() {
  const [manifest, setManifest] = useState<Manifest>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/manifest`)
      .then((r) => r.json())
      .then(setManifest)
      .catch(() => setManifest({}))
      .finally(() => setLoading(false));
  }, []);

  return { manifest, categories: Object.keys(manifest), loading };
}
