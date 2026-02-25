import { Link } from 'react-router-dom';

interface Integration {
  icon: string;
  name: string;
  category: string;
  description: string;
  apiProvider: string;
  apiUrl: string;
  keyRequired: 'free' | 'optional' | 'required' | 'builtin';
  tools: string[];
  agentVisible: boolean;
  useCases: string[];
}

const INTEGRATIONS: Integration[] = [
  {
    icon: '⛅',
    name: 'Weather',
    category: 'Environment',
    description:
      'Fetch current conditions, 5-day / 3-hour forecasts, and weather by GPS coordinates. The agent uses this to show contextual banners like "Carry an umbrella today" or activate rain-gear promotions.',
    apiProvider: 'OpenWeatherMap',
    apiUrl: 'https://openweathermap.org/api',
    keyRequired: 'required',
    tools: ['get_current_weather', 'get_weather_forecast', 'get_weather_by_coords'],
    agentVisible: true,
    useCases: ['Weather-triggered promotions', 'Activity suggestions', 'Seasonal campaigns'],
  },
  {
    icon: '💨',
    name: 'Air Quality',
    category: 'Environment',
    description:
      'Real-time Air Quality Index (AQI) plus per-pollutant readings (PM2.5, PM10, O₃, NO₂, SO₂, CO). Great for health apps, outdoor activity reminders, or air-purifier upsells.',
    apiProvider: 'WAQI (World Air Quality Index)',
    apiUrl: 'https://aqicn.org/api/',
    keyRequired: 'optional',
    tools: ['get_air_quality_by_city', 'get_air_quality_by_coords'],
    agentVisible: true,
    useCases: ['Health warnings', 'Mask/purifier promotions', 'Outdoor event alerts'],
  },
  {
    icon: '🌍',
    name: 'Earthquake',
    category: 'Safety',
    description:
      'Live seismic event data from the USGS Earthquake Hazards API. No API key needed. Query recent worldwide earthquakes or within a radius of any coordinates.',
    apiProvider: 'USGS Earthquake Hazards',
    apiUrl: 'https://earthquake.usgs.gov/fdsnws/',
    keyRequired: 'free',
    tools: ['get_recent_earthquakes', 'get_earthquakes_by_area'],
    agentVisible: true,
    useCases: ['Safety alerts', 'Emergency information banners', 'Disaster-preparedness apps'],
  },
  {
    icon: '💱',
    name: 'Exchange Rates',
    category: 'Finance',
    description:
      'ECB foreign exchange rates for 30+ currencies updated daily, plus live amount conversion between any pair. Powered by the free Frankfurter API — no API key required.',
    apiProvider: 'Frankfurter (ECB data)',
    apiUrl: 'https://www.frankfurter.app',
    keyRequired: 'free',
    tools: ['get_exchange_rates', 'convert_currency'],
    agentVisible: true,
    useCases: ['Travel apps', 'E-commerce price display', 'Currency converter widgets'],
  },
  {
    icon: '🕌',
    name: 'Prayer Times',
    category: 'Lifestyle',
    description:
      'Islamic prayer times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha, Midnight) for any city or GPS coordinates. Supports 12 calculation methods including Diyanet (Turkey), ISNA, MWL, Makkah and more.',
    apiProvider: 'Aladhan',
    apiUrl: 'https://aladhan.com/prayer-times-api',
    keyRequired: 'free',
    tools: ['get_prayer_times', 'get_prayer_times_by_coords', 'get_prayer_methods'],
    agentVisible: true,
    useCases: ['Muslim lifestyle apps', 'Reminder widgets', 'Iftar countdown banners'],
  },
  {
    icon: '📅',
    name: 'Holidays & Special Days',
    category: 'Calendar',
    description:
      '24+ special days (national holidays, awareness days, cultural events) in the built-in database. The agent can suggest a themed widget for any holiday automatically.',
    apiProvider: 'Built-in database',
    apiUrl: '',
    keyRequired: 'builtin',
    tools: ['get_today_holidays', 'get_holidays_by_date', 'get_upcoming_holidays', 'get_holidays_for_month', 'suggest_widget_for_holiday'],
    agentVisible: true,
    useCases: ['Holiday-themed promotions', 'Seasonal campaigns', 'Event reminders'],
  },
  {
    icon: '🔥',
    name: 'Viral Trends',
    category: 'Social',
    description:
      'Current viral topics from Google Trends RSS and Twitter/X Trending. Filter by category (dance, music, challenge, meme, sports) and platform. Use it to ride trending waves in your app.',
    apiProvider: 'Google Trends + Twitter/X',
    apiUrl: 'https://trends.google.com',
    keyRequired: 'optional',
    tools: ['get_trends', 'suggest_from_trends'],
    agentVisible: true,
    useCases: ['Trend-riding campaigns', 'Social content widgets', 'Viral challenge banners'],
  },
  {
    icon: '📰',
    name: 'News Headlines',
    category: 'Content',
    description:
      'Top headlines from 80+ countries, filtered by category (business, sports, tech, health, entertainment). Powered by NewsAPI.org.',
    apiProvider: 'NewsAPI.org',
    apiUrl: 'https://newsapi.org',
    keyRequired: 'required',
    tools: ['get_data_sources'],
    agentVisible: true,
    useCases: ['News digest widgets', 'Breaking news banners', 'Category-based headlines'],
  },
  {
    icon: '🔮',
    name: 'Horoscope',
    category: 'Lifestyle',
    description:
      'AI-generated daily horoscope content for all 12 zodiac signs, created by Gemini. Useful for lifestyle and astrology apps to show personalized content.',
    apiProvider: 'Gemini AI (built-in)',
    apiUrl: '',
    keyRequired: 'builtin',
    tools: ['get_data_sources'],
    agentVisible: true,
    useCases: ['Astrology apps', 'Daily motivation widgets', 'Personalized content'],
  },
];

const KEY_LABELS: Record<Integration['keyRequired'], { label: string; color: string }> = {
  free:     { label: 'Free · No Key',    color: '#22c55e' },
  optional: { label: 'Free · Key Optional', color: '#22c55e' },
  required: { label: 'API Key Required', color: '#f59e0b' },
  builtin:  { label: 'Built-in',         color: '#6366f1' },
};

const CATEGORIES = ['All', ...Array.from(new Set(INTEGRATIONS.map((i) => i.category)))];

export default function Integrations() {
  return (
    <main id="main-content" style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px 80px' }}>
      {/* Header */}
      <section style={{ textAlign: 'center', paddingTop: 64, paddingBottom: 48 }}>
        <div style={styles.badge}>MCP Data Sources</div>
        <h1 style={styles.h1}>Live Integrations</h1>
        <p style={styles.subtitle}>
          Every widget the AI agent creates can be backed by real-time data. These integrations run
          inside the MCP server and are available to the Gemini agent automatically.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <span style={styles.stat}><strong>9</strong> data sources</span>
          <span style={styles.stat}><strong>29</strong> MCP tools</span>
          <span style={styles.stat}><strong>17</strong> agent-visible</span>
          <span style={styles.stat}><strong>5</strong> free / no key</span>
        </div>
      </section>

      {/* Cards grid */}
      <div style={styles.grid}>
        {INTEGRATIONS.map((intg) => {
          const kl = KEY_LABELS[intg.keyRequired];
          return (
            <article
              key={intg.name}
              aria-label={`${intg.name} integration`}
              style={styles.card}
            >
              {/* Card header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 14 }}>
                <span aria-hidden="true" style={{ fontSize: 36, lineHeight: 1, flexShrink: 0 }}>{intg.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                    <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>{intg.name}</h2>
                    <span style={{
                      fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 20,
                      background: `${kl.color}22`, color: kl.color, border: `1px solid ${kl.color}44`,
                    }}>{kl.label}</span>
                  </div>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', background: 'rgba(99,102,241,0.1)', padding: '2px 8px', borderRadius: 4 }}>
                    {intg.category}
                  </span>
                </div>
              </div>

              <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
                {intg.description}
              </p>

              {/* API source */}
              <div style={{ fontSize: 13, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ color: 'var(--text-muted)' }}>API:</span>
                {intg.apiUrl ? (
                  <a href={intg.apiUrl} target="_blank" rel="noopener noreferrer"
                    style={{ color: '#6366f1', fontWeight: 500 }}>
                    {intg.apiProvider} ↗
                  </a>
                ) : (
                  <span style={{ fontWeight: 500 }}>{intg.apiProvider}</span>
                )}
              </div>

              {/* MCP tools */}
              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  MCP Tools
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {intg.tools.map((t) => (
                    <code key={t} style={styles.toolChip}>{t}</code>
                  ))}
                </div>
              </div>

              {/* Use cases */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Use Cases
                </div>
                <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {intg.useCases.map((uc) => (
                    <li key={uc} style={styles.useCase}>{uc}</li>
                  ))}
                </ul>
              </div>
            </article>
          );
        })}
      </div>

      {/* Bottom CTA */}
      <section style={{ textAlign: 'center', paddingTop: 64 }}>
        <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>Want more integrations?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 28, maxWidth: 480, margin: '0 auto 28px' }}>
          The MCP server is extensible. Any free or paid API can be added as a new data source in minutes
          using the 4-step pattern documented in MCP-ENTEGRASYONLARI.md.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>
          Get Started →
        </Link>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  badge: {
    display: 'inline-block', fontSize: 13, fontWeight: 500, color: '#6366f1',
    background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)',
    borderRadius: 20, padding: '6px 16px', marginBottom: 20,
  },
  h1: { fontSize: 'clamp(28px, 4vw, 42px)' as unknown as number, fontWeight: 800, lineHeight: 1.2, marginBottom: 16 },
  subtitle: { fontSize: 16, color: 'var(--text-muted)', maxWidth: 580, margin: '0 auto 28px', lineHeight: 1.6 },
  stat: {
    display: 'inline-flex', alignItems: 'center', gap: 4,
    fontSize: 14, padding: '6px 14px', borderRadius: 20,
    background: 'var(--bg-card)', border: '1px solid var(--border)',
  },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 20 },
  card: {
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', padding: 24,
  },
  toolChip: {
    fontSize: 11, fontWeight: 600, padding: '3px 8px', borderRadius: 4,
    background: 'rgba(99,102,241,0.1)', color: '#818cf8',
    border: '1px solid rgba(99,102,241,0.2)', fontFamily: 'monospace',
  },
  useCase: {
    fontSize: 12, padding: '4px 10px', borderRadius: 6,
    background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)',
    color: 'var(--text-muted)',
  },
  btnPrimary: {
    display: 'inline-flex', alignItems: 'center', padding: '12px 28px',
    fontSize: 15, fontWeight: 600, color: '#fff', background: '#6366f1',
    borderRadius: 'var(--radius-sm)', border: 'none',
  },
};
