import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";

export default function Orders() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      setOrders(await api.listOrders());
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

  async function setStatus(id, status) {
    try {
      await api.updateOrderStatus(id, status);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page orders-page">
      <div className="page-head">
        <h1>Orders</h1>
        <p>{isAdmin ? "All customer orders." : "Your recent checkouts."}</p>
      </div>
      {error ? <p className="alert">{error}</p> : null}

      {orders.length === 0 ? (
        <div className="empty-state">
          <h2>No orders yet</h2>
          <Link to="/shop" className="btn primary">
            Shop now
          </Link>
        </div>
      ) : (
        <ul className="order-list">
          {orders.map((order) => (
            <li key={order.id} className="order-block">
              <div className="order-top">
                <div>
                  <h3>Order #{order.id}</h3>
                  <p className="muted">
                    {new Date(order.created_at).toLocaleString()} · {order.status}
                  </p>
                </div>
                <strong>${Number(order.total_amount).toFixed(2)}</strong>
              </div>
              <p className="muted">{order.shipping_address}</p>
              <ul className="order-items">
                {order.items.map((item) => (
                  <li key={item.id}>
                    Product #{item.product_id} × {item.quantity} — $
                    {Number(item.subtotal).toFixed(2)}
                  </li>
                ))}
              </ul>
              {isAdmin && order.status !== "cancelled" ? (
                <div className="order-actions">
                  {["confirmed", "shipped", "delivered", "cancelled"].map((status) => (
                    <button
                      key={status}
                      type="button"
                      className="btn ghost sm"
                      onClick={() => setStatus(order.id, status)}
                    >
                      Mark {status}
                    </button>
                  ))}
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
