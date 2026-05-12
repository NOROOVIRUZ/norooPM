export interface Product {
  rank: number;
  name: string;
  price: string;
  price_usd: number;
  thumbnail: string;
  product_url: string;
  platform: "amazon" | "amazon_jp" | "aliexpress" | "jd" | "rakuten" | "coupang" | "shopee_tw" | "shopee_sg" | "flipkart";
  rating?: number;
  reviews?: number;
  sales?: string;
}

export interface ScrapeResult {
  category: string;
  scraped_at: string;
  platforms: {
    amazon?: Product[];
    amazon_jp?: Product[];
    aliexpress?: Product[];
    jd?: Product[];
    rakuten?: Product[];
    coupang?: Product[];
    shopee_tw?: Product[];
    shopee_sg?: Product[];
    flipkart?: Product[];
  };
}

export interface Manifest {
  [category: string]: {
    last_updated: string;
  };
}
