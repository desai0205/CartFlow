import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="hero">
      <div className="hero-copy reveal">
        <p className="brand-mark">CartFlow</p>
        <h1>Everyday goods, ordered in a flow.</h1>
        <p className="lede">
          Browse curated products, fill your cart, and checkout without the noise.
        </p>
        <div className="hero-cta">
          <Link to="/shop" className="btn primary lg">
            Start shopping
          </Link>
          <Link to="/register" className="btn ghost lg">
            Create account
          </Link>
        </div>
      </div>
      <div
        className="hero-visual reveal delay"
        role="img"
        aria-label="Shelves of everyday home goods in soft natural light"
        style={{
          backgroundImage:
            "linear-gradient(120deg, rgba(15, 40, 32, 0.35), rgba(15, 40, 32, 0.1)), url('https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1600&q=80')",
        }}
      />
    </section>
  );
}
