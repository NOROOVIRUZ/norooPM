export interface Product {
  rank: number;
  name: string;
  price: string;
  price_usd: number;
  thumbnail: string;
  product_url: string;
  platform: "amazon" | "aliexpress" | "jd";
  rating?: number;
  reviews?: number;
  sales?: string;
}

export interface ScrapeResult {
  category: string;
  scraped_at: string;
  platforms: {
    amazon?: Product[];
    aliexpress?: Product[];
    jd?: Product[];
  };
}

export interface Manifest {
  [category: string]: {
    last_updated: string;
  };
}
