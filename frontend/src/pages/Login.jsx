import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
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
        <h1>Sign in</h1>
        <p className="muted">Welcome back to CartFlow.</p>
        {error ? <p className="alert">{error}</p> : null}
        <label>
          Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button type="submit" className="btn primary lg" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="muted">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </form>
    </section>
  );
}
