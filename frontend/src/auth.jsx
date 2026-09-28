import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, clearSession, getStoredUser, setSession } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [cartCount, setCartCount] = useState(0);
  const [ready, setReady] = useState(false);

  async function refreshCart() {
    if (!localStorage.getItem("cartflow_token")) {
      setCartCount(0);
      return;
    }
    try {
      const cart = await api.getCart();
      setCartCount(cart.total_items || 0);
    } catch {
      setCartCount(0);
    }
  }

  useEffect(() => {
    async function boot() {
      const token = localStorage.getItem("cartflow_token");
      if (!token) {
        setReady(true);
        return;
      }
      try {
        const me = await api.me();
        setUser(me);
        setSession(token, me);
        await refreshCart();
      } catch {
        clearSession();
        setUser(null);
      } finally {
        setReady(true);
      }
    }
    boot();
  }, []);

  const value = useMemo(
    () => ({
      user,
      ready,
      cartCount,
      refreshCart,
      async login(email, password) {
        const data = await api.login(email, password);
        setSession(data.access_token, data.user);
        setUser(data.user);
        await refreshCart();
        return data.user;
      },
      async register(payload) {
        await api.register(payload);
        const data = await api.login(payload.email, payload.password);
        setSession(data.access_token, data.user);
        setUser(data.user);
        await refreshCart();
        return data.user;
      },
      logout() {
        clearSession();
        setUser(null);
        setCartCount(0);
      },
      isAdmin: user?.role === "admin",
    }),
    [user, ready, cartCount]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
