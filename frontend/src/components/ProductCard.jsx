import { Link } from "react-router-dom";
import { productTone } from "../api";

export default function ProductCard({ product, onAdd, busy }) {
  const [a, b] = productTone(product.id);
  return (
    <article className="product-tile">
      <Link to={`/shop/${product.id}`} className="product-media" style={{ background: `linear-gradient(145deg, ${a}, ${b})` }}>
        <span>{product.name.slice(0, 1)}</span>
      </Link>
      <div className="product-body">
        <p className="product-meta">{product.category?.name || "General"}</p>
        <h3>
          <Link to={`/shop/${product.id}`}>{product.name}</Link>
        </h3>
        <div className="product-row">
          <strong>${Number(product.price).toFixed(2)}</strong>
          <button
            type="button"
            className="btn primary sm"
            disabled={busy || product.stock < 1}
            onClick={() => onAdd(product)}
          >
            {product.stock < 1 ? "Sold out" : "Add"}
          </button>
        </div>
      </div>
    </article>
  );
}
