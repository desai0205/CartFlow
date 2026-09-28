const API = "/api/v1";

function getToken() {
  return localStorage.getItem("cartflow_token");
}

export function setSession(token, user) {
  localStorage.setItem("cartflow_token", token);
  localStorage.setItem("cartflow_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("cartflow_token");
  localStorage.removeItem("cartflow_user");
}

export function getStoredUser() {
  const raw = localStorage.getItem("cartflow_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }

  if (!res.ok) {
    const detail = data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(data?.errors)
          ? data.errors.map((e) => e.message).join(", ")
          : "Request failed";
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  register: (payload) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: async (email, password) => {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);
    return request("/auth/login", { method: "POST", body, headers: {} });
  },
  me: () => request("/auth/me"),
  listCategories: () => request("/categories"),
  createCategory: (payload) =>
    request("/categories", { method: "POST", body: JSON.stringify(payload) }),
  listProducts: (params = {}) => {
    const q = new URLSearchParams();
    if (params.category_id) q.set("category_id", params.category_id);
    if (params.limit) q.set("limit", params.limit);
    if (params.active_only === false) q.set("active_only", "false");
    const qs = q.toString();
    return request(`/products${qs ? `?${qs}` : ""}`);
  },
  getProduct: (id) => request(`/products/${id}`),
  createProduct: (payload) =>
    request("/products", { method: "POST", body: JSON.stringify(payload) }),
  updateProduct: (id, payload) =>
    request(`/products/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  updateStock: (id, stock) =>
    request(`/products/${id}/stock`, { method: "PATCH", body: JSON.stringify({ stock }) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: "DELETE" }),
  getCart: () => request("/cart"),
  addToCart: (product_id, quantity = 1) =>
    request("/cart/items", {
      method: "POST",
      body: JSON.stringify({ product_id, quantity }),
    }),
  updateCartItem: (id, quantity) =>
    request(`/cart/items/${id}`, { method: "PUT", body: JSON.stringify({ quantity }) }),
  removeCartItem: (id) => request(`/cart/items/${id}`, { method: "DELETE" }),
  clearCart: () => request("/cart", { method: "DELETE" }),
  createOrder: (shipping_address) =>
    request("/orders", { method: "POST", body: JSON.stringify({ shipping_address }) }),
  listOrders: () => request("/orders"),
  updateOrderStatus: (id, status) =>
    request(`/orders/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};

export function productTone(id) {
  const tones = [
    ["#1b4332", "#95d5b2"],
    ["#0f3d3e", "#7ec8c4"],
    ["#2d4a22", "#b5c99a"],
    ["#1a3a4a", "#8ecae6"],
    ["#3d2c1e", "#d4a373"],
    ["#2c3e50", "#a8dadc"],
  ];
  return tones[id % tones.length];
}
