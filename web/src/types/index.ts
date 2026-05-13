export interface Product {
  rank: number;
  name: string;
  price: string;
  price_usd: number;
  thumbnail: string;
  product_url: string;
  platform: string;
  rating?: number;
  reviews?: number;
  sales?: string;
}

export interface ScrapeResult {
  category: string;
  scraped_at: string;
  platforms: {
    naver?: Product[];
    amazon_jp?: Product[];
    [key: string]: Product[] | undefined;
  };
}

export interface Manifest {
  [category: string]: {
    last_updated: string;
  };
}
