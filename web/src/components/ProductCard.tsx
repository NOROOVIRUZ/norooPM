import { Product } from "../types";

const PLATFORM_COLORS: Record<string, string> = {
  amazon: "#FF9900",
  amazon_jp: "#FF6600",
  aliexpress: "#E62E2E",
  jd: "#CC0000",
  rakuten: "#BF0000",
  coupang: "#1A83FF",
  shopee_tw: "#EE4D2D",
  shopee_sg: "#EE4D2D",
  flipkart: "#2874F0",
};

const PLATFORM_LABELS: Record<string, string> = {
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

export default function ProductCard({ product }: { product: Product }) {
  const color = PLATFORM_COLORS[product.platform] ?? "#888";
  const label = PLATFORM_LABELS[product.platform] ?? product.platform;

  return (
    <a
      href={product.product_url}
      target="_blank"
      rel="noopener noreferrer"
      className="product-card"
    >
      <div className="rank-badge">#{product.rank}</div>
      <div className="thumbnail-wrap">
        <img
          src={product.thumbnail}
          alt={product.name}
          onError={(e) => {
            (e.target as HTMLImageElement).src = "/placeholder.png";
          }}
        />
      </div>
      <div className="product-info">
        <span className="platform-badge" style={{ background: color }}>
          {label}
        </span>
        <p className="product-name">{product.name}</p>
        <p className="product-price">{product.price}</p>
        {product.rating && (
          <p className="product-meta">
            ⭐ {product.rating}
            {product.reviews ? ` (${product.reviews.toLocaleString()})` : ""}
          </p>
        )}
        {product.sales && <p className="product-meta">📦 {product.sales}</p>}
      </div>
    </a>
  );
}
