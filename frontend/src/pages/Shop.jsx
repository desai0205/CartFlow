import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import ProductCard from "../components/ProductCard";

export default function Shop() {
  const { user, refreshCart } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState("");
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [cats, items] = await Promise.all([
          api.listCategories(),
          api.listProducts({
            category_id: categoryId || undefined,
            limit: 50,
          }),
        ]);
        setCategories(cats);
        setProducts(items);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [categoryId]);

  async function handleAdd(product) {
    if (!user) {
      navigate("/login");
      return;
    }
    setBusyId(product.id);
    setError("");
    try {
      await api.addToCart(product.id, 1);
      await refreshCart();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="page shop-page">
      <div className="page-head">
        <h1>Shop</h1>
        <p>Find something useful and add it to your cart.</p>
      </div>

      <div className="filters">
        <button
          type="button"
          className={!categoryId ? "filter active" : "filter"}
          onClick={() => setCategoryId("")}
        >
          All
        </button>
        {categories.map((c) => (
          <button
            key={c.id}
            type="button"
            className={categoryId === String(c.id) ? "filter active" : "filter"}
            onClick={() => setCategoryId(String(c.id))}
          >
            {c.name}
          </button>
        ))}
      </div>

      {error ? <p className="alert">{error}</p> : null}
      {loading ? <p className="muted">Loading products…</p> : null}

      {!loading && products.length === 0 ? (
        <div className="empty-state">
          <h2>No products yet</h2>
          <p>An admin can add categories and products from the Admin page.</p>
          <Link to="/admin" className="btn primary">
            Go to Admin
          </Link>
        </div>
      ) : (
        <div className="product-grid">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} onAdd={handleAdd} busy={busyId === p.id} />
          ))}
        </div>
      )}
    </section>
  );
}
