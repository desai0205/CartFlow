import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Layout from "./components/Layout";
import Admin from "./pages/Admin";
import Cart from "./pages/Cart";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Orders from "./pages/Orders";
import ProductDetail from "./pages/ProductDetail";
import Register from "./pages/Register";
import Shop from "./pages/Shop";

function Gate({ children }) {
  const { ready } = useAuth();
  if (!ready) return <p className="page muted">Loading CartFlow…</p>;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Gate>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="shop" element={<Shop />} />
              <Route path="shop/:id" element={<ProductDetail />} />
              <Route path="cart" element={<Cart />} />
              <Route path="orders" element={<Orders />} />
              <Route path="admin" element={<Admin />} />
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Gate>
      </BrowserRouter>
    </AuthProvider>
  );
}
