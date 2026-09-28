import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";

export default function Cart() {
  const { user, refreshCart } = useAuth();
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [address, setAddress] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const data = await api.getCart();
      setCart(data);
      await refreshCart();
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    load();
  }, [user]);

  async function updateQty(itemId, quantity) {
    setBusy(true);
    setError("");
    try {
      const data = await api.updateCartItem(itemId, quantity);
      setCart(data);
      await refreshCart();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(itemId) {
    setBusy(true);
    try {
      const data = await api.removeCartItem(itemId);
      setCart(data);
      await refreshCart();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function checkout(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.createOrder(address);
      await refreshCart();
      navigate("/orders");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (!cart) return <p className="page muted">Loading cart…</p>;

  return (
    <section className="page cart-page">
      <div className="page-head">
        <h1>Your cart</h1>
        <p>{cart.total_items} item{cart.total_items === 1 ? "" : "s"} ready to checkout.</p>
      </div>

      {error ? <p className="alert">{error}</p> : null}

      {cart.items.length === 0 ? (
        <div className="empty-state">
          <h2>Cart is empty</h2>
          <Link to="/shop" className="btn primary">
            Browse shop
          </Link>
        </div>
      ) : (
        <div className="cart-layout">
          <ul className="cart-list">
            {cart.items.map((item) => (
              <li key={item.id} className="cart-row">
                <div>
                  <h3>{item.product.name}</h3>
                  <p className="muted">${Number(item.product.price).toFixed(2)} each</p>
                </div>
                <div className="cart-controls">
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    disabled={busy}
                    onChange={(e) => updateQty(item.id, Math.max(1, Number(e.target.value) || 1))}
                  />
                  <strong>${Number(item.subtotal).toFixed(2)}</strong>
                  <button type="button" className="btn ghost sm" onClick={() => remove(item.id)}>
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>

          <form className="checkout-panel" onSubmit={checkout}>
            <h2>Checkout</h2>
            <p className="total">Total ${Number(cart.total_amount).toFixed(2)}</p>
            <label>
              Shipping address
              <textarea
                required
                minLength={5}
                rows={3}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Street, city, postal code"
              />
            </label>
            <button type="submit" className="btn primary lg" disabled={busy}>
              Place order
            </button>
          </form>
        </div>
      )}
    </section>
  );
}
