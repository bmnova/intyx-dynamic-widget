import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import type { WidgetResponse, SuggestWidgetResponse, ColorPalette } from '../types';

interface CatalogEntry {
  type: string;
  icon: string;
  label: string;
  desc: string;
}

const WIDGET_CATALOG: CatalogEntry[] = [
  { type: 'hero_image', icon: '🖼', label: 'Hero Image', desc: 'Full-width hero with overlay title and CTA button' },
  { type: 'promotional', icon: '🏷', label: 'Promotional', desc: 'Campaign card with badge, discount info' },
  { type: 'carousel', icon: '🎠', label: 'Carousel', desc: 'Horizontal scrolling multi-content cards' },
  { type: 'countdown_banner', icon: '⏳', label: 'Countdown', desc: 'Countdown timer banner for campaigns' },
  { type: 'contextual', icon: '🌤', label: 'Contextual', desc: 'Context-aware card (weather, horoscope, etc.)' },
  { type: 'informational', icon: 'ℹ️', label: 'Informational', desc: 'Notice / announcement card' },
  { type: 'banner', icon: '📢', label: 'Banner', desc: 'Simple text banner with emoji' },
  { type: 'title_subtitle_image', icon: '📋', label: 'Title + Image', desc: 'Card with title, subtitle, and image' },
  { type: 'clickable_image_link', icon: '🔗', label: 'Clickable Image', desc: 'Tappable image with link redirect' },
  { type: 'icon_text_action', icon: '⚡', label: 'Icon + Action', desc: 'Icon, text, and action button' },
  { type: 'rating', icon: '⭐', label: 'Rating', desc: 'Star rating card for user feedback' },
  { type: 'poll', icon: '📊', label: 'Poll', desc: 'Single-choice voting card' },
  { type: 'social_proof', icon: '👥', label: 'Social Proof', desc: 'Metric, testimonial, user count' },
  { type: 'progress', icon: '📈', label: 'Progress', desc: 'Progress bar with goal tracking' },
  { type: 'profile', icon: '👤', label: 'Profile', desc: 'User spotlight card' },
  { type: 'functional', icon: '🎯', label: 'Functional', desc: 'Action-focused card with buttons' },
];

type TabKey = 'catalog' | 'prompt' | 'preview';

function formatTtl(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)}h`;
  return `${Math.round(seconds / 86400)}d`;
}

function CountdownDisplay({ endTime }: { endTime?: string }) {
  const getRemaining = () => {
    if (!endTime) return '00:00:00';
    const diff = new Date(endTime).getTime() - Date.now();
    if (diff <= 0) return '00:00:00';
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };
  const [remaining, setRemaining] = useState(getRemaining);
  useEffect(() => {
    if (!endTime) return;
    const timer = setInterval(() => setRemaining(getRemaining()), 1000);
    return () => clearInterval(timer);
  }, [endTime]);
  return <>{remaining}</>;
}

export default function WidgetStudio() {
  const apiKey = localStorage.getItem('intyx_api_key') || 'dev-key';
  const [selected, setSelected] = useState<string[]>([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SuggestWidgetResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabKey>('catalog');

  const toggleWidget = (type: string) => {
    setSelected((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const selectAll = () => setSelected(WIDGET_CATALOG.map((w) => w.type));
  const clearSelection = () => setSelected([]);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please write a prompt describing your app and what widgets you want.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    const context = {
      developer_task: prompt.trim(),
      preferred_widget_types: selected.length > 0 ? selected : undefined,
      current_date: new Date().toISOString(),
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/ai/suggest-widget`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
        body: JSON.stringify({ context }),
      });
      if (!res.ok) {
        const errData: { error?: string } = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Request failed (${res.status})`);
      }
      const data: SuggestWidgetResponse = await res.json();
      setResult(data);
      setTab('preview');
    } catch (err) {
      const isNetworkErr = err instanceof TypeError;
      setError(
        isNetworkErr
          ? 'Backend unreachable. Set VITE_API_URL in Vercel environment variables to point to your deployed API.'
          : (err as Error).message
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main id="main-content" style={{ maxWidth: 1000, margin: '0 auto', padding: '60px 24px' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Widget Studio</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Select widget types, describe your app, and let AI generate the perfect widgets for you.
      </p>

      {/* Tabs */}
      <div role="tablist" aria-label="Widget studio steps" style={styles.tabs}>
        {([
          { key: 'catalog' as TabKey, label: '1. Select Widgets', count: selected.length },
          { key: 'prompt' as TabKey, label: '2. Write Prompt' },
          { key: 'preview' as TabKey, label: '3. Preview', disabled: !result },
        ] as const).map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            aria-controls={`tabpanel-${t.key}`}
            id={`tab-${t.key}`}
            onClick={() => !('disabled' in t && t.disabled) && setTab(t.key)}
            aria-disabled={'disabled' in t && t.disabled ? true : undefined}
            style={{
              ...styles.tab,
              borderColor: tab === t.key ? '#6366f1' : 'transparent',
              color: tab === t.key ? '#fff' : ('disabled' in t && t.disabled) ? '#52525b' : '#a1a1aa',
              cursor: ('disabled' in t && t.disabled) ? 'default' : 'pointer',
            }}
          >
            {t.label}
            {'count' in t && t.count > 0 && (
              <span aria-label={`${t.count} selected`} style={styles.tabBadge}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {error && (
        <div role="alert" aria-live="assertive" style={styles.errorBanner}>
          {error}
          <button onClick={() => setError(null)} aria-label="Dismiss error" style={styles.errorClose}>x</button>
        </div>
      )}

      {/* Tab: Widget Catalog */}
      {tab === 'catalog' && (
        <div id="tabpanel-catalog" role="tabpanel" aria-labelledby="tab-catalog">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
              {selected.length === 0
                ? 'No filter — AI will choose from all types'
                : `${selected.length} type(s) selected`}
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={selectAll} style={styles.btnGhost}>Select All</button>
              {selected.length > 0 && (
                <button onClick={clearSelection} style={styles.btnGhost}>Clear</button>
              )}
            </div>
          </div>
          <div style={styles.catalogGrid}>
            {WIDGET_CATALOG.map((w) => {
              const isSelected = selected.includes(w.type);
              return (
                <button
                  key={w.type}
                  onClick={() => toggleWidget(w.type)}
                  style={{
                    ...styles.widgetCard,
                    borderColor: isSelected ? '#6366f1' : 'var(--border)',
                    background: isSelected ? 'rgba(99,102,241,0.08)' : 'var(--bg-card)',
                  }}
                >
                  <div style={styles.widgetIcon}>{w.icon}</div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{w.label}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>{w.desc}</div>
                  {isSelected && <div style={styles.checkMark}>✓</div>}
                </button>
              );
            })}
          </div>
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <button onClick={() => setTab('prompt')} style={styles.btnPrimary}>
              Next: Write Prompt →
            </button>
          </div>
        </div>
      )}

      {/* Tab: Prompt */}
      {tab === 'prompt' && (
        <div id="tabpanel-prompt" role="tabpanel" aria-labelledby="tab-prompt">
          <div style={styles.card}>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Describe Your App</h2>
            <p id="prompt-hint" style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Tell the AI agent what your app does and what kind of widgets you want.
            </p>
            <label htmlFor="studio-prompt" className="visually-hidden">Describe your app and desired widgets</label>
            <textarea
              id="studio-prompt"
              aria-describedby="prompt-hint"
              placeholder={'Example: My app is a fashion e-commerce app. I want to show:\n- Weather-based outfit suggestions\n- Seasonal campaign banners'}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              style={styles.textarea}
              rows={8}
            />

            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>Quick templates:</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {[
                  'Fashion app — weather-based outfit suggestions',
                  'Food delivery — meal recommendations by time of day',
                  'Fitness app — daily motivation and progress tracking',
                  'E-commerce — seasonal promotions and flash sales',
                  'News app — trending topics and breaking alerts',
                  'Travel app — destination weather and packing tips',
                ].map((tpl, i) => (
                  <button key={i} onClick={() => setPrompt(tpl)} style={styles.templateChip}>
                    {tpl}
                  </button>
                ))}
              </div>
            </div>

            {selected.length > 0 && (
              <div style={styles.selectionSummary}>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Widget filter:</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                  {selected.map((type) => {
                    const w = WIDGET_CATALOG.find((c) => c.type === type);
                    return (
                      <span key={type} style={styles.selectedChip}>
                        {w?.icon} {w?.label}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
              <button onClick={() => setTab('catalog')} style={styles.btnGhost}>← Back to Catalog</button>
              <button
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                style={{ ...styles.btnPrimary, opacity: loading || !prompt.trim() ? 0.5 : 1 }}
              >
                {loading ? 'Generating...' : 'Generate Widgets'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Preview */}
      {tab === 'preview' && result && (
        <div id="tabpanel-preview" role="tabpanel" aria-labelledby="tab-preview">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700 }}>
              Generated Widgets ({result.widgets?.length || 0})
            </h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => setTab('prompt')} style={styles.btnGhost}>Edit Prompt</button>
              <button onClick={handleGenerate} disabled={loading} style={styles.btnPrimary}>
                {loading ? 'Regenerating...' : 'Regenerate'}
              </button>
            </div>
          </div>

          {result.widgets && result.widgets.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {result.widgets.map((widget, i) => (
                <div key={widget.id || i} style={styles.previewCard}>
                  <div style={styles.previewHeader}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={styles.previewIcon}>
                        {WIDGET_CATALOG.find((c) => c.type === widget.type)?.icon || '📦'}
                      </span>
                      <div>
                        <div style={{ fontSize: 15, fontWeight: 600 }}>
                          {widget.params?.title || widget.params?.text || widget.type}
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{widget.type}</div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                      {widget.common?.priority != null && (
                        <span style={styles.priorityBadge}>P{widget.common.priority}</span>
                      )}
                      {widget.common?.ttl_seconds != null && (
                        <span style={styles.ttlBadge} title={`TTL: ${widget.common.ttl_seconds} seconds`}>
                          ⏱ {widget.common.ttl_seconds === 0 ? '∞' : formatTtl(widget.common.ttl_seconds as number)}
                        </span>
                      )}
                      {widget.common?.dismissible != null && (
                        <span style={widget.common.dismissible ? styles.dismissibleBadge : styles.stickyBadge}>
                          {widget.common.dismissible ? '✕ Dismissible' : '📌 Sticky'}
                        </span>
                      )}
                      {widget.common?.color_palette && (
                        <span style={styles.paletteBadge} title="Custom color palette applied">
                          🎨 Themed
                        </span>
                      )}
                      <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 10, background: 'var(--success-muted)', color: 'var(--success)', fontWeight: 600 }}>
                        Ready
                      </span>
                    </div>
                  </div>
                  <div style={styles.previewBody}>
                    <WidgetPreview widget={widget} />
                  </div>
                  <details style={{ marginTop: 12 }}>
                    <summary style={{ fontSize: 13, color: 'var(--text-muted)', cursor: 'pointer' }}>View JSON</summary>
                    <pre style={styles.codeBlock}>{JSON.stringify(widget, null, 2)}</pre>
                  </details>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ ...styles.card, textAlign: 'center', padding: 48 }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🤷</div>
              <div style={{ color: 'var(--text-muted)' }}>No widgets generated. Try a different prompt.</div>
            </div>
          )}

          <div style={{ ...styles.card, marginTop: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Save as Agent Task</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Save this prompt as a reusable agent task for your Flutter app.
            </p>
            <SaveAsTask prompt={prompt} apiKey={apiKey} />
          </div>

          <details style={{ marginTop: 16 }}>
            <summary style={styles.rawToggle}>Full API Response</summary>
            <pre style={{ ...styles.codeBlock, marginTop: 8 }}>{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      )}

      <div style={{ height: 80 }} />
    </main>
  );
}

function WidgetPreview({ widget }: { widget: WidgetResponse }) {
  const { type, params = {}, common = {} } = widget;
  const palette = (common.color_palette ?? {}) as ColorPalette;

  const accentColor = palette.primary ?? '#6366f1';
  const accentTextColor = palette.on_primary ?? '#fff';
  const mutedColor = palette.on_surface ? `${palette.on_surface}99` : 'var(--text-muted)';

  const box: React.CSSProperties = {
    background: palette.surface ?? palette.background ?? '#0c0c0e',
    border: `1px solid ${palette.primary ? `${palette.primary}33` : 'var(--border)'}`,
    borderRadius: palette.border_radius != null ? palette.border_radius : 10,
    padding: 20,
    color: palette.on_surface ?? palette.on_background ?? 'var(--text)',
  };

  const actionLinkStyle: React.CSSProperties = {
    fontSize: 11,
    color: mutedColor,
    marginLeft: 6,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    maxWidth: 180,
    display: 'inline-block',
    verticalAlign: 'middle',
  };

  if (type === 'banner') {
    return (
      <div style={{ ...box, textAlign: 'center', fontSize: 15 }}>
        {params.emoji && <span style={{ marginRight: 8, fontSize: 20 }}>{String(params.emoji)}</span>}
        {String(params.text ?? '')}
        {params.action_text && (
          <div style={{ marginTop: 10 }}>
            <span style={{ fontSize: 13, color: accentColor, fontWeight: 600 }}>{String(params.action_text)} →</span>
          </div>
        )}
      </div>
    );
  }

  if (type === 'hero_image') {
    return (
      <div style={{
        ...box,
        backgroundImage: params.image_url ? `url(${String(params.image_url)})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        minHeight: 120,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
      }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{String(params.title ?? '')}</div>
        {params.button_text && (
          <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 13, color: accentColor, fontWeight: 600 }}>{String(params.button_text)} →</span>
            {params.button_action && (
              <span style={actionLinkStyle} title={String(params.button_action)}>
                {String(params.button_action)}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }

  if (type === 'promotional') {
    return (
      <div style={box}>
        {params.image_url && (
          <div style={{
            height: 80,
            borderRadius: 6,
            marginBottom: 10,
            backgroundImage: `url(${String(params.image_url)})`,
            backgroundSize: params.image_fit === 'contain' ? 'contain' : 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            background: params.image_url ? undefined : '#27272a',
          }} />
        )}
        {params.badge_text && <span style={previewBadgeStyle}>{String(params.badge_text)}</span>}
        <div style={{ fontSize: 16, fontWeight: 700, marginTop: 8 }}>{String(params.title ?? '')}</div>
        <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.description ?? '')}</div>
        {params.action_url && (
          <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ fontSize: 12, color: accentColor }}>🔗</span>
            <span style={{ ...actionLinkStyle, color: accentColor }} title={String(params.action_url)}>
              {String(params.action_url)}
            </span>
          </div>
        )}
      </div>
    );
  }

  if (type === 'countdown_banner') {
    return (
      <div style={{ ...box, textAlign: 'center' }}>
        <div style={{ fontSize: 15, fontWeight: 600 }}>{String(params.title ?? '')}</div>
        {params.end_time && (
          <div style={{ fontSize: 11, color: mutedColor, marginTop: 2 }}>
            ends {new Date(String(params.end_time)).toLocaleString()}
          </div>
        )}
        <div style={{ fontSize: 24, fontWeight: 800, color: accentColor, margin: '8px 0', fontVariantNumeric: 'tabular-nums' }}>
          <CountdownDisplay endTime={params.end_time ? String(params.end_time) : undefined} />
        </div>
        {params.button_text && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            <span style={{ fontSize: 13, color: palette.secondary ?? '#818cf8' }}>{String(params.button_text)}</span>
            {params.button_action && (
              <span style={actionLinkStyle} title={String(params.button_action)}>
                {String(params.button_action)}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }

  if (type === 'informational') {
    const severityColors: Record<string, { bg: string; fg: string; icon: string }> = {
      warning: { bg: 'rgba(251,146,60,0.1)', fg: '#f97316', icon: '⚠️' },
      error:   { bg: 'rgba(239,68,68,0.1)',  fg: '#ef4444', icon: '🔴' },
      success: { bg: 'rgba(34,197,94,0.1)',  fg: '#22c55e', icon: '✅' },
      info:    { bg: 'rgba(99,130,241,0.1)', fg: '#818cf8', icon: 'ℹ️' },
    };
    const sev = String(params.severity ?? 'info');
    const s = severityColors[sev] ?? severityColors.info;
    return (
      <div style={{ ...box, background: s.bg, border: `1px solid ${s.fg}33` }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <span style={{ fontSize: 20, lineHeight: 1 }}>{s.icon}</span>
          <div>
            {params.title && <div style={{ fontSize: 15, fontWeight: 600, color: s.fg }}>{String(params.title)}</div>}
            {params.message && <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.message)}</div>}
          </div>
        </div>
      </div>
    );
  }

  if (type === 'rating') {
    return (
      <div style={{ ...box, textAlign: 'center' }}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{String(params.title ?? '')}</div>
        <div style={{ fontSize: 28, margin: '8px 0', letterSpacing: 4, color: palette.secondary ?? '#f59e0b' }}>
          {'★'.repeat(Number(params.max_stars) || 5)}
        </div>
        {params.subtitle && <div style={{ fontSize: 12, color: mutedColor }}>{String(params.subtitle)}</div>}
      </div>
    );
  }

  if (type === 'poll') {
    const options = Array.isArray(params.options) ? params.options : [];
    return (
      <div style={box}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>{String(params.question ?? '')}</div>
        {options.map((opt, i) => (
          <div key={i} style={{ padding: '8px 12px', marginBottom: 6, border: `1px solid ${accentColor}33`, borderRadius: 6, fontSize: 13, cursor: 'pointer' }}>
            {typeof opt === 'string' ? opt : (opt as { label?: string; text?: string }).label ?? (opt as { label?: string; text?: string }).text ?? JSON.stringify(opt)}
          </div>
        ))}
      </div>
    );
  }

  if (type === 'progress') {
    const pct = Math.min(100, Math.max(0, Number(params.progress) * (Number(params.progress) <= 1 ? 100 : 1) || 0));
    return (
      <div style={box}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{String(params.title ?? '')}</div>
        {params.subtitle && <div style={{ fontSize: 12, color: mutedColor, marginTop: 2 }}>{String(params.subtitle)}</div>}
        <div style={{ height: 8, borderRadius: 4, background: '#27272a', marginTop: 10, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: accentColor, borderRadius: 4 }} />
        </div>
        <div style={{ fontSize: 12, color: mutedColor, marginTop: 6 }}>{String(params.progress_label ?? `${Math.round(pct)}%`)}</div>
        {(params.action_text || params.action_url) && (
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
            {params.action_text && (
              <span style={{ fontSize: 13, color: accentColor, fontWeight: 600 }}>{String(params.action_text)} →</span>
            )}
            {params.action_url && (
              <span style={actionLinkStyle} title={String(params.action_url)}>{String(params.action_url)}</span>
            )}
          </div>
        )}
      </div>
    );
  }

  if (type === 'contextual') {
    const ctxIconMap: Record<string, string> = {
      weather: '🌤', location: '📍', calendar: '📅', clock: '🕐',
      star: '⭐', info: 'ℹ️', warning: '⚠️', horoscope: '✨',
      crypto: '💰', news: '📰', sports: '⚽', prayer: '🕌',
      earthquake: '🌍', air: '💨', uv: '☀️',
    };
    const iconVal = String(params.icon ?? 'info');
    const ctxIcon = ctxIconMap[iconVal] ?? iconVal;
    return (
      <div style={box}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <div style={{ fontSize: 28, lineHeight: 1, flexShrink: 0 }}>{ctxIcon}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 600 }}>{String(params.title ?? '')}</div>
            <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.content ?? '')}</div>
            {params.source && (
              <div style={{ fontSize: 11, color: `${mutedColor}99`, marginTop: 6 }}>
                via {String(params.source)}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (type === 'functional') {
    const fnActions = Array.isArray(params.actions) ? params.actions : [];
    return (
      <div style={box}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>{String(params.title ?? '')}</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {(fnActions.length > 0 ? fnActions : [{ label: 'Action', style: 'primary' }]).map((a, i) => {
            const act = typeof a === 'string' ? { label: a, style: 'primary' } : a as { label?: string; style?: string; action?: string; url?: string };
            const isPrimary = !act.style || act.style === 'primary';
            const actionTarget = act.action ?? act.url;
            return (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 2 }}>
                <span style={{
                  fontSize: 13, fontWeight: 600, padding: '7px 16px', borderRadius: 8,
                  background: isPrimary ? accentColor : 'transparent',
                  color: isPrimary ? accentTextColor : accentColor,
                  border: isPrimary ? 'none' : `1px solid ${accentColor}`,
                }}>
                  {String(act.label ?? '')}
                </span>
                {actionTarget && (
                  <span style={{ ...actionLinkStyle, marginLeft: 0, fontSize: 10 }} title={String(actionTarget)}>
                    {String(actionTarget)}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (type === 'carousel') {
    const carouselItems = Array.isArray(params.items) ? params.items : [];
    const displayItems = carouselItems.length > 0
      ? carouselItems.slice(0, 4)
      : [{ title: String(params.title ?? 'Card 1') }, { title: 'Card 2' }, { title: 'Card 3' }];
    return (
      <div style={box}>
        {params.title && carouselItems.length > 0 && (
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>{String(params.title)}</div>
        )}
        <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 4 }}>
          {displayItems.map((item, i) => {
            const card = typeof item === 'string'
              ? { title: item }
              : item as { title?: string; description?: string; image_url?: string; image_fit?: string; link_url?: string };
            const bgSize = card.image_fit === 'contain' ? 'contain' : 'cover';
            return (
              <div key={i} style={{ minWidth: 130, background: '#18181b', border: `1px solid ${accentColor}22`, borderRadius: 8, padding: 12, flexShrink: 0 }}>
                {card.image_url
                  ? <div style={{ height: 56, borderRadius: 6, marginBottom: 8, backgroundImage: `url(${String(card.image_url)})`, backgroundSize: bgSize, backgroundPosition: 'center', backgroundRepeat: 'no-repeat' }} />
                  : <div style={{ height: 40, borderRadius: 6, marginBottom: 8, background: '#27272a' }} />
                }
                <div style={{ fontSize: 12, fontWeight: 600 }}>{String(card.title ?? `Item ${i + 1}`)}</div>
                {card.description && <div style={{ fontSize: 11, color: mutedColor, marginTop: 3 }}>{String(card.description)}</div>}
                {card.link_url && (
                  <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                    <span style={{ fontSize: 10, color: accentColor }}>🔗</span>
                    <span style={{ fontSize: 10, color: accentColor, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 90 }} title={String(card.link_url)}>
                      {String(card.link_url)}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (type === 'title_subtitle_image') {
    const bgSize = params.image_fit === 'contain' ? 'contain' : 'cover';
    return (
      <div style={{ ...box, padding: 0, overflow: 'hidden' }}>
        {params.image_url
          ? <div style={{ height: 100, backgroundImage: `url(${String(params.image_url)})`, backgroundSize: bgSize, backgroundPosition: 'center', backgroundRepeat: 'no-repeat' }} />
          : <div style={{ height: 80, background: '#27272a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#52525b', fontSize: 13 }}>Image</div>
        }
        <div style={{ padding: 14 }}>
          <div style={{ fontSize: 15, fontWeight: 600 }}>{String(params.title ?? '')}</div>
          {params.subtitle && <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.subtitle)}</div>}
        </div>
      </div>
    );
  }

  if (type === 'clickable_image_link') {
    const target = params.link_url ?? params.action_url;
    return (
      <div style={{ ...box, padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '14px 14px 10px' }}>
          <div style={{ fontSize: 15, fontWeight: 600 }}>{String(params.title ?? '')}</div>
        </div>
        {params.image_url
          ? <div style={{ height: 80, backgroundImage: `url(${String(params.image_url)})`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
          : <div style={{ height: 64, background: '#27272a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#52525b', fontSize: 13 }}>Image</div>
        }
        <div style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 14, color: accentColor }}>🔗</span>
          <span style={{ fontSize: 13, color: accentColor, textDecoration: 'underline', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
            title={target ? String(target) : undefined}>
            {String(params.link_text ?? target ?? '')}
          </span>
        </div>
      </div>
    );
  }

  if (type === 'icon_text_action') {
    const itaIconMap: Record<string, string> = {
      info: 'ℹ️', warning: '⚠️', error: '🔴', success: '✅', star: '⭐',
      favorite: '❤️', notification: '🔔', settings: '⚙️', shopping: '🛒',
      delivery: '🚚', location: '📍', calendar: '📅', clock: '🕐',
      weather: '🌤', offer: '🏷', gift: '🎁', campaign: '📢', target: '🎯',
    };
    const iconVal = String(params.icon ?? 'info');
    const itaIcon = itaIconMap[iconVal] ?? iconVal;
    return (
      <div style={box}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 44, height: 44, borderRadius: 10, background: `${accentColor}22`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0 }}>
            {itaIcon}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 600 }}>{String(params.title ?? '')}</div>
            {params.description && <div style={{ fontSize: 12, color: mutedColor, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{String(params.description)}</div>}
            {params.action_url && !params.action_text && (
              <div style={{ fontSize: 10, color: accentColor, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={String(params.action_url)}>
                {String(params.action_url)}
              </div>
            )}
          </div>
          {params.action_text && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2, flexShrink: 0 }}>
              <span style={{ fontSize: 13, color: accentColor, fontWeight: 600, whiteSpace: 'nowrap' }}>{String(params.action_text)} →</span>
              {params.action_url && (
                <span style={{ fontSize: 10, color: mutedColor, maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={String(params.action_url)}>
                  {String(params.action_url)}
                </span>
              )}
            </div>
          )}
          {!params.action_text && params.action_url && (
            <span style={{ color: accentColor, fontSize: 18, flexShrink: 0 }}>›</span>
          )}
        </div>
      </div>
    );
  }

  if (type === 'social_proof') {
    const testimonialText = params.testimonial ?? params.quote;
    const authorName = params.author_name ?? params.author;
    const avatarUrl = params.avatar_url;
    return (
      <div style={box}>
        {params.metric && (
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 4 }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: accentColor }}>{String(params.metric)}</div>
            {params.metric_label && (
              <div style={{ fontSize: 13, color: mutedColor, fontWeight: 500 }}>{String(params.metric_label)}</div>
            )}
          </div>
        )}
        {testimonialText && (
          <div style={{ fontSize: 13, color: mutedColor, margin: '10px 0', fontStyle: 'italic', borderLeft: `2px solid ${accentColor}`, paddingLeft: 10 }}>
            "{String(testimonialText)}"
          </div>
        )}
        {authorName && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {avatarUrl
              ? <div style={{ width: 28, height: 28, borderRadius: '50%', backgroundImage: `url(${String(avatarUrl)})`, backgroundSize: 'cover', backgroundPosition: 'center', flexShrink: 0 }} />
              : <div style={{ width: 28, height: 28, borderRadius: '50%', background: '#27272a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0 }}>👤</div>
            }
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{String(authorName)}</div>
              {params.author_title && <div style={{ fontSize: 11, color: mutedColor }}>{String(params.author_title)}</div>}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (type === 'profile') {
    return (
      <div style={{ ...box, textAlign: 'center' }}>
        <div style={{
          width: 56, height: 56, borderRadius: '50%', margin: '0 auto 10px',
          backgroundImage: params.avatar_url ? `url(${String(params.avatar_url)})` : undefined,
          backgroundSize: 'cover', backgroundPosition: 'center',
          background: params.avatar_url ? undefined : '#27272a',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 26,
        }}>
          {!params.avatar_url && '👤'}
        </div>
        <div style={{ fontSize: 16, fontWeight: 700 }}>{String(params.name ?? '')}</div>
        {params.title && <div style={{ fontSize: 13, color: accentColor, marginTop: 2 }}>{String(params.title)}</div>}
        {params.subtitle && <div style={{ fontSize: 12, color: mutedColor, marginTop: 4 }}>{String(params.subtitle)}</div>}
        {(params.action_text || params.action_url) && (
          <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            {params.action_text && (
              <span style={{ fontSize: 13, fontWeight: 600, padding: '6px 20px', borderRadius: 20, background: accentColor, color: accentTextColor }}>
                {String(params.action_text)}
              </span>
            )}
            {params.action_url && (
              <span style={{ fontSize: 10, color: mutedColor, maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={String(params.action_url)}>
                {String(params.action_url)}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={box}>
      {params.title && <div style={{ fontSize: 15, fontWeight: 600 }}>{String(params.title)}</div>}
      {params.subtitle && <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.subtitle)}</div>}
      {params.description && <div style={{ fontSize: 13, color: mutedColor, marginTop: 4 }}>{String(params.description)}</div>}
      {params.text && <div style={{ fontSize: 14, marginTop: 4 }}>{String(params.text)}</div>}
      {params.action_text && (
        <span style={{ fontSize: 13, color: accentColor, fontWeight: 600, marginTop: 8, display: 'inline-block' }}>
          {String(params.action_text)} →
        </span>
      )}
    </div>
  );
}

const previewBadgeStyle: React.CSSProperties = {
  fontSize: 11, fontWeight: 700, color: '#f59e0b',
  background: 'rgba(245,158,11,0.15)', padding: '3px 10px', borderRadius: 12,
};

function SaveAsTask({ prompt, apiKey }: { prompt: string; apiKey: string }) {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, task: prompt, name: name.trim() || 'Widget Studio Task' }),
      });
      if (res.ok) setSaved(true);
    } catch { /* best effort */ } finally {
      setSaving(false);
    }
  };

  if (saved) {
    return <div style={{ color: 'var(--success)', fontSize: 14, fontWeight: 600 }}>Saved! Go to Agent Tasks to manage it.</div>;
  }

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <input type="text" placeholder="Task name" value={name} onChange={(e) => setName(e.target.value)} style={{ ...styles.input, flex: 1, marginBottom: 0 }} />
      <button onClick={handleSave} disabled={saving} style={styles.btnPrimary}>{saving ? 'Saving...' : 'Save'}</button>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  tabs: { display: 'flex', gap: 0, marginBottom: 24, borderBottom: '1px solid var(--border)' },
  tab: { padding: '12px 20px', fontSize: 14, fontWeight: 600, background: 'none', border: 'none', borderBottom: '2px solid transparent', display: 'flex', alignItems: 'center', gap: 8 },
  tabBadge: { fontSize: 11, fontWeight: 700, color: '#fff', background: '#6366f1', padding: '1px 7px', borderRadius: 10 },
  card: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 24 },
  catalogGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 },
  widgetCard: { position: 'relative', textAlign: 'left', padding: 16, borderRadius: 'var(--radius)', border: '1px solid var(--border)', cursor: 'pointer', transition: 'border-color 0.15s, background 0.15s' },
  widgetIcon: { fontSize: 24, marginBottom: 8 },
  checkMark: { position: 'absolute', top: 10, right: 10, width: 22, height: 22, borderRadius: '50%', background: '#6366f1', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700 },
  input: { width: '100%', padding: '10px 14px', fontSize: 14, background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', marginBottom: 12, outline: 'none' },
  textarea: { width: '100%', padding: '14px 16px', fontSize: 14, background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', marginBottom: 16, outline: 'none', resize: 'vertical', fontFamily: 'inherit', lineHeight: 1.6 },
  templateChip: { padding: '6px 12px', fontSize: 12, color: 'var(--text-muted)', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 20, cursor: 'pointer', textAlign: 'left' },
  selectionSummary: { padding: 12, background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)', borderRadius: 8 },
  selectedChip: { fontSize: 12, padding: '3px 10px', background: 'var(--primary-muted)', color: '#818cf8', borderRadius: 14, fontWeight: 500 },
  btnPrimary: { padding: '10px 24px', fontSize: 14, fontWeight: 600, color: '#fff', background: '#6366f1', border: 'none', borderRadius: 8, cursor: 'pointer' },
  btnGhost: { padding: '8px 16px', fontSize: 13, fontWeight: 500, color: 'var(--text-muted)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 8, cursor: 'pointer' },
  errorBanner: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', marginBottom: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', fontSize: 14 },
  errorClose: { background: 'none', border: 'none', color: '#ef4444', fontWeight: 700, fontSize: 16, cursor: 'pointer' },
  previewCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 20 },
  previewHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  previewIcon: { width: 40, height: 40, borderRadius: 10, background: 'var(--primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 },
  previewBody: {},
  priorityBadge: { fontSize: 11, fontWeight: 700, color: '#6366f1', background: 'var(--primary-muted)', padding: '2px 8px', borderRadius: 10 },
  ttlBadge: { fontSize: 11, fontWeight: 700, color: '#f59e0b', background: 'rgba(245,158,11,0.12)', padding: '2px 8px', borderRadius: 10 },
  dismissibleBadge: { fontSize: 11, fontWeight: 600, color: '#94a3b8', background: 'rgba(148,163,184,0.1)', padding: '2px 8px', borderRadius: 10 },
  stickyBadge: { fontSize: 11, fontWeight: 600, color: '#818cf8', background: 'rgba(99,102,241,0.1)', padding: '2px 8px', borderRadius: 10 },
  paletteBadge: { fontSize: 11, fontWeight: 600, color: '#c084fc', background: 'rgba(192,132,252,0.1)', padding: '2px 8px', borderRadius: 10 },
  codeBlock: { background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 8, padding: '14px 18px', fontSize: 12, lineHeight: 1.6, color: '#c4b5fd', fontFamily: "'JetBrains Mono', 'Fira Code', monospace", overflow: 'auto', whiteSpace: 'pre', margin: 0, marginTop: 8 },
  rawToggle: { fontSize: 14, color: 'var(--text-muted)', cursor: 'pointer' },
};
