import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";

const emptyProduct = {
  name: "",
  description: "",
  price: "",
  stock: 10,
  category_id: "",
};

export default function Admin() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [catName, setCatName] = useState("");
  const [productForm, setProductForm] = useState(emptyProduct);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const [cats, items] = await Promise.all([
      api.listCategories(),
      api.listProducts({ limit: 100, active_only: false }),
    ]);
    // listProducts always filters active_only by default on API - that's fine for admin view of active
    setCategories(cats);
    setProducts(items);
    if (!productForm.category_id && cats[0]) {
      setProductForm((prev) => ({ ...prev, category_id: String(cats[0].id) }));
    }
  }

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (!isAdmin) {
      navigate("/shop");
      return;
    }
    load().catch((err) => setError(err.message));
  }, [user, isAdmin]);

  async function addCategory(e) {
    e.preventDefault();
    setError("");
    setNotice("");
    try {
      await api.createCategory({ name: catName, description: "" });
      setCatName("");
      setNotice("Category created.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function addProduct(e) {
    e.preventDefault();
    setError("");
    setNotice("");
    try {
      await api.createProduct({
        name: productForm.name,
        description: productForm.description || null,
        price: productForm.price,
        stock: Number(productForm.stock),
        category_id: Number(productForm.category_id),
      });
      setProductForm((prev) => ({ ...emptyProduct, category_id: prev.category_id }));
      setNotice("Product created.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function softDelete(id) {
    try {
      await api.deleteProduct(id);
      setNotice("Product removed from shop.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page admin-page">
      <div className="page-head">
        <h1>Admin</h1>
        <p>Manage categories, products, and stock.</p>
      </div>

      {error ? <p className="alert">{error}</p> : null}
      {notice ? <p className="notice">{notice}</p> : null}

      <div className="admin-grid">
        <form className="panel" onSubmit={addCategory}>
          <h2>New category</h2>
          <label>
            Name
            <input required value={catName} onChange={(e) => setCatName(e.target.value)} />
          </label>
          <button type="submit" className="btn primary">
            Add category
          </button>
        </form>

        <form className="panel" onSubmit={addProduct}>
          <h2>New product</h2>
          <label>
            Name
            <input
              required
              value={productForm.name}
              onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
            />
          </label>
          <label>
            Description
            <textarea
              rows={2}
              value={productForm.description}
              onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
            />
          </label>
          <div className="form-row">
            <label>
              Price
              <input
                required
                type="number"
                step="0.01"
                min="0.01"
                value={productForm.price}
                onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
              />
            </label>
            <label>
              Stock
              <input
                required
                type="number"
                min="0"
                value={productForm.stock}
                onChange={(e) => setProductForm({ ...productForm, stock: e.target.value })}
              />
            </label>
          </div>
          <label>
            Category
            <select
              required
              value={productForm.category_id}
              onChange={(e) => setProductForm({ ...productForm, category_id: e.target.value })}
            >
              <option value="">Select…</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="btn primary" disabled={!categories.length}>
            Add product
          </button>
        </form>
      </div>

      <div className="panel">
        <h2>Products</h2>
        {products.length === 0 ? (
          <p className="muted">No products yet.</p>
        ) : (
          <ul className="admin-products">
            {products.map((p) => (
              <li key={p.id}>
                <div>
                  <strong>{p.name}</strong>
                  <p className="muted">
                    ${Number(p.price).toFixed(2)} · stock {p.stock} · {p.category?.name}
                  </p>
                </div>
                <button type="button" className="btn ghost sm" onClick={() => softDelete(p.id)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
