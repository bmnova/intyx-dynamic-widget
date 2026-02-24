import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <main
      id="main-content"
      aria-labelledby="not-found-heading"
      style={{
        maxWidth: 600,
        margin: '0 auto',
        padding: '120px 24px',
        textAlign: 'center',
      }}
    >
      <p
        aria-hidden="true"
        style={{ fontSize: 72, fontWeight: 800, color: 'var(--text-muted)', marginBottom: 8 }}
      >
        404
      </p>
      <h1
        id="not-found-heading"
        style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}
      >
        Page Not Found
      </h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link
        to="/"
        aria-label="Go back to Intyx home page"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '12px 28px',
          fontSize: 15,
          fontWeight: 600,
          color: '#fff',
          background: '#6366f1',
          borderRadius: 8,
          border: 'none',
          textDecoration: 'none',
        }}
      >
        Back to Home
      </Link>
    </main>
  );
}
