import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={{
      maxWidth: 600,
      margin: '0 auto',
      padding: '120px 24px',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: 72, fontWeight: 800, color: 'var(--text-muted)', marginBottom: 8 }}>
        404
      </div>
      <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>
        Sayfa Bulunamadi
      </h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Aradiginiz sayfa mevcut degil veya tasindi.
      </p>
      <Link
        to="/"
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
        Ana Sayfaya Don
      </Link>
    </div>
  );
}
