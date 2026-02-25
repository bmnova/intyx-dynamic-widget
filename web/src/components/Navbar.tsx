import { Link, useLocation } from 'react-router-dom';

interface NavLink {
  to: string;
  label: string;
}

const links: NavLink[] = [
  { to: '/', label: 'Home' },
  { to: '/integrations', label: 'Integrations' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/widget-studio', label: 'Studio' },
  { to: '/agent-tasks', label: 'Agent Tasks' },
  { to: '/analytics', label: 'Analytics' },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav aria-label="Main navigation" style={styles.nav}>
      <div style={styles.inner}>
        <Link to="/" aria-label="Intyx home" style={styles.logo}>
          <span aria-hidden="true" style={styles.logoIcon}>◆</span> intyx
        </Link>
        <div role="list" style={styles.links}>
          {links.map((l) => (
            <div role="listitem" key={l.to}>
              <Link
                to={l.to}
                aria-current={pathname === l.to ? 'page' : undefined}
                style={{
                  ...styles.link,
                  color: pathname === l.to ? '#6366f1' : '#a1a1aa',
                }}
              >
                {l.label}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </nav>
  );
}

const styles: Record<string, React.CSSProperties> = {
  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 50,
    backdropFilter: 'blur(12px)',
    background: 'rgba(9,9,11,0.8)',
    borderBottom: '1px solid var(--border)',
  },
  inner: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '0 24px',
    height: 64,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logo: {
    fontSize: 20,
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  logoIcon: {
    color: '#6366f1',
    fontSize: 24,
  },
  links: {
    display: 'flex',
    gap: 32,
  },
  link: {
    fontSize: 14,
    fontWeight: 500,
    transition: 'color 0.2s',
  },
};
