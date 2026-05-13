import { useEffect, useState } from "react";
import { Manifest } from "../types";

const GITHUB_RAW = "https://raw.githubusercontent.com/NOROOVIRUZ/norooPM/main/data";

export function useManifest() {
  const [manifest, setManifest] = useState<Manifest>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${GITHUB_RAW}/manifest.json`)
      .then((r) => r.json())
      .then(setManifest)
      .catch(() => setManifest({}))
      .finally(() => setLoading(false));
  }, []);

  return { manifest, categories: Object.keys(manifest), loading };
}
