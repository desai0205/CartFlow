import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(form);
      navigate("/shop");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="page auth-page">
      <form className="auth-form" onSubmit={onSubmit}>
        <h1>Join CartFlow</h1>
        <p className="muted">Create an account to shop and track orders.</p>
        {error ? <p className="alert">{error}</p> : null}
        <label>
          Full name
          <input
            required
            value={form.full_name}
            onChange={(e) => update("full_name", e.target.value)}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            required
            minLength={6}
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
          />
        </label>
        <button type="submit" className="btn primary lg" disabled={busy}>
          {busy ? "Creating…" : "Create account"}
        </button>
        <p className="muted">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </section>
  );
}
