import { useEffect } from 'react';

export default function Toast({ type = 'error', message, onClose, duration = 4000 }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const colors = {
    error: { bg: 'rgba(239,68,68,0.15)', border: '#ef4444', text: '#fca5a5' },
    success: { bg: 'rgba(34,197,94,0.15)', border: '#22c55e', text: '#86efac' },
    info: { bg: 'rgba(99,102,241,0.15)', border: '#6366f1', text: '#a5b4fc' },
  };
  const c = colors[type] || colors.error;

  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        background: c.bg,
        border: `1px solid ${c.border}`,
        borderRadius: 10,
        padding: '14px 20px',
        color: c.text,
        fontSize: 14,
        fontWeight: 500,
        maxWidth: 380,
        backdropFilter: 'blur(12px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        animation: 'slideIn 0.3s ease',
      }}
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        aria-label="Dismiss notification"
        style={{
          background: 'none',
          border: 'none',
          color: c.text,
          fontSize: 18,
          cursor: 'pointer',
          padding: 0,
          lineHeight: 1,
        }}
      >
        &times;
      </button>
    </div>
  );
}
