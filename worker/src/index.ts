const GITHUB_RAW = "https://raw.githubusercontent.com/NOROOVIRUZ/norooPM/main/data";
const REPO_API = "https://api.github.com/repos/NOROOVIRUZ/norooPM/actions/workflows/scrape.yml/dispatches";
const CACHE_TTL = 3600; // 1시간

export interface Env {
  NOOROOPM_CACHE: KVNamespace;
  GITHUB_TOKEN: string;
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_CHAT_ID: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const path = url.pathname;

    if (path === "/api/manifest") {
      return proxyJson(`${GITHUB_RAW}/manifest.json`, env, cors);
    }

    if (path.startsWith("/api/data/")) {
      const category = decodeURIComponent(path.replace("/api/data/", ""));
      return proxyJson(`${GITHUB_RAW}/${category}/latest.json`, env, cors, category);
    }

    if (path === "/api/trigger" && request.method === "POST") {
      return triggerScrape(request, env, cors);
    }

    return new Response("norooPM API", { headers: cors });
  },
};

async function proxyJson(
  rawUrl: string,
  env: Env,
  cors: Record<string, string>,
  cacheKey?: string
): Promise<Response> {
  const key = cacheKey ?? rawUrl;
  const cached = await env.NOOROOPM_CACHE.get(key);
  if (cached) {
    return new Response(cached, {
      headers: { ...cors, "Content-Type": "application/json", "X-Cache": "HIT" },
    });
  }

  const res = await fetch(rawUrl);
  if (!res.ok) {
    // manifest가 없으면 latest.json 대신 날짜 파일 목록으로 폴백 시도
    return new Response(JSON.stringify({ error: "not found" }), {
      status: 404,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  const body = await res.text();
  await env.NOOROOPM_CACHE.put(key, body, { expirationTtl: CACHE_TTL });
  return new Response(body, {
    headers: { ...cors, "Content-Type": "application/json", "X-Cache": "MISS" },
  });
}

async function triggerScrape(
  request: Request,
  env: Env,
  cors: Record<string, string>
): Promise<Response> {
  const body = await request.json<{ categories?: string; platforms?: string }>();

  const res = await fetch(REPO_API, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ref: "main",
      inputs: {
        categories: body.categories ?? "all",
        platforms: body.platforms ?? "amazon aliexpress jd",
      },
    }),
  });

  if (res.status === 204) {
    await fetch(
      `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          text: `🔍 norooPM 수집 시작됨\n카테고리: ${body.categories ?? "전체"}\n약 3~5분 후 완료 알림 드릴게요.`,
        }),
      }
    );
    return new Response(JSON.stringify({ ok: true }), {
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ ok: false, status: res.status }), {
    status: 500,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
