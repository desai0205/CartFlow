import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, productTone } from "../api";
import { useAuth } from "../auth";

export default function ProductDetail() {
  const { id } = useParams();
  const { user, refreshCart } = useAuth();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [qty, setQty] = useState(1);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .getProduct(id)
      .then(setProduct)
      .catch((err) => setError(err.message));
  }, [id]);

  async function add() {
    if (!user) {
      navigate("/login");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.addToCart(product.id, qty);
      await refreshCart();
      navigate("/cart");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!product && !error) return <p className="page muted">Loading…</p>;
  if (!product) return <p className="page alert">{error}</p>;

  const [a, b] = productTone(product.id);

  return (
    <section className="page detail-page">
      <Link to="/shop" className="back-link">
        ← Back to shop
      </Link>
      <div className="detail-grid">
        <div
          className="detail-media"
          style={{ background: `linear-gradient(145deg, ${a}, ${b})` }}
        >
          <span>{product.name.slice(0, 1)}</span>
        </div>
        <div className="detail-copy">
          <p className="product-meta">{product.category?.name || "General"}</p>
          <h1>{product.name}</h1>
          <p className="lede">{product.description || "No description provided."}</p>
          <p className="price">${Number(product.price).toFixed(2)}</p>
          <p className="muted">{product.stock} in stock</p>
          {error ? <p className="alert">{error}</p> : null}
          <div className="detail-actions">
            <label>
              Qty
              <input
                type="number"
                min="1"
                max={product.stock}
                value={qty}
                onChange={(e) => setQty(Math.max(1, Number(e.target.value) || 1))}
              />
            </label>
            <button
              type="button"
              className="btn primary lg"
              disabled={busy || product.stock < 1}
              onClick={add}
            >
              {product.stock < 1 ? "Sold out" : "Add to cart"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
