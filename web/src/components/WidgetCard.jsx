export default function WidgetCard({ icon, title, description, tag }) {
  return (
    <div style={styles.card}>
      <div style={styles.iconWrap}>
        <span style={styles.icon}>{icon}</span>
      </div>
      <h3 style={styles.title}>{title}</h3>
      <p style={styles.desc}>{description}</p>
      {tag && <span style={styles.tag}>{tag}</span>}
    </div>
  );
}

const styles = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
    transition: 'border-color 0.2s, transform 0.2s',
    cursor: 'default',
  },
  iconWrap: {
    width: 48,
    height: 48,
    borderRadius: 'var(--radius-sm)',
    background: 'var(--primary-muted)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    fontSize: 22,
  },
  icon: {},
  title: {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 8,
  },
  desc: {
    fontSize: 14,
    color: 'var(--text-muted)',
    lineHeight: 1.5,
  },
  tag: {
    display: 'inline-block',
    marginTop: 12,
    fontSize: 12,
    fontWeight: 500,
    color: 'var(--primary)',
    background: 'var(--primary-muted)',
    padding: '4px 10px',
    borderRadius: 20,
  },
};
