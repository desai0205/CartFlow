import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";

export default function Layout() {
  const { user, cartCount, logout, isAdmin } = useAuth();

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          CartFlow
        </Link>
        <nav className="nav">
          <NavLink to="/shop">Shop</NavLink>
          <NavLink to="/cart">
            Cart{cartCount > 0 ? <span className="badge">{cartCount}</span> : null}
          </NavLink>
          {user ? <NavLink to="/orders">Orders</NavLink> : null}
          {isAdmin ? <NavLink to="/admin">Admin</NavLink> : null}
        </nav>
        <div className="topbar-actions">
          {user ? (
            <>
              <span className="user-chip">{user.full_name.split(" ")[0]}</span>
              <button type="button" className="btn ghost" onClick={logout}>
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn ghost">
                Sign in
              </Link>
              <Link to="/register" className="btn primary">
                Join
              </Link>
            </>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <p>CartFlow — shop simply.</p>
      </footer>
    </div>
  );
}
