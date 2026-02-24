import { useState } from 'react';
import { API_BASE_URL } from '../config';

const WIDGET_CATALOG = [
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

export default function WidgetStudio() {
  const apiKey = localStorage.getItem('intyx_api_key') || 'dev-key';
  const [selected, setSelected] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('catalog'); // catalog | prompt | preview

  const toggleWidget = (type) => {
    setSelected((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const selectAll = () => {
    setSelected(WIDGET_CATALOG.map((w) => w.type));
  };

  const clearSelection = () => {
    setSelected([]);
  };

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
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ context }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setResult(data);
      setTab('preview');
    } catch (err) {
      const isNetworkErr = err instanceof TypeError;
      setError(
        isNetworkErr
          ? 'Backend unreachable. Set VITE_API_URL in Vercel environment variables to point to your deployed API.'
          : err.message
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
        {[
          { key: 'catalog', label: '1. Select Widgets', count: selected.length },
          { key: 'prompt', label: '2. Write Prompt' },
          { key: 'preview', label: '3. Preview', disabled: !result },
        ].map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            aria-controls={`tabpanel-${t.key}`}
            id={`tab-${t.key}`}
            onClick={() => !t.disabled && setTab(t.key)}
            aria-disabled={t.disabled ? true : undefined}
            style={{
              ...styles.tab,
              borderColor: tab === t.key ? '#6366f1' : 'transparent',
              color: tab === t.key ? '#fff' : t.disabled ? '#52525b' : '#a1a1aa',
              cursor: t.disabled ? 'default' : 'pointer',
            }}
          >
            {t.label}
            {t.count > 0 && <span aria-label={`${t.count} selected`} style={styles.tabBadge}>{t.count}</span>}
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
              The more detail you give, the better the results.
            </p>
            <label htmlFor="studio-prompt" className="visually-hidden">Describe your app and desired widgets</label>
            <textarea
              id="studio-prompt"
              aria-describedby="prompt-hint"
              placeholder={'Example: My app is a fashion e-commerce app. I want to show:\n- Weather-based outfit suggestions\n- Seasonal campaign banners\n- Trending style recommendations\n- User rating prompts after purchase'}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              style={styles.textarea}
              rows={8}
            />

            {/* Quick prompt templates */}
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
                  <button
                    key={i}
                    onClick={() => setPrompt(tpl)}
                    style={styles.templateChip}
                  >
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
              <button onClick={() => setTab('catalog')} style={styles.btnGhost}>
                ← Back to Catalog
              </button>
              <button
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                style={{
                  ...styles.btnPrimary,
                  opacity: loading || !prompt.trim() ? 0.5 : 1,
                }}
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
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      {widget.common?.priority && (
                        <span style={styles.priorityBadge}>P{widget.common.priority}</span>
                      )}
                      <span style={{
                        fontSize: 11,
                        padding: '2px 8px',
                        borderRadius: 10,
                        background: 'var(--success-muted)',
                        color: 'var(--success)',
                        fontWeight: 600,
                      }}>
                        Ready
                      </span>
                    </div>
                  </div>
                  <div style={styles.previewBody}>
                    <WidgetPreview widget={widget} />
                  </div>
                  <details style={{ marginTop: 12 }}>
                    <summary style={{ fontSize: 13, color: 'var(--text-muted)', cursor: 'pointer' }}>
                      View JSON
                    </summary>
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

          {/* Save as Agent Task */}
          <div style={{ ...styles.card, marginTop: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Save as Agent Task</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              Save this prompt as a reusable agent task. Your Flutter app will automatically
              resolve it and show these widgets to your users.
            </p>
            <SaveAsTask prompt={prompt} apiKey={apiKey} />
          </div>

          {/* Raw JSON */}
          <details style={{ marginTop: 16 }}>
            <summary style={styles.rawToggle}>Full API Response</summary>
            <pre style={{ ...styles.codeBlock, marginTop: 8 }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}

      <div style={{ height: 80 }} />
    </main>
  );
}

/* ── Inline widget preview component ─────────────────────────────── */

function WidgetPreview({ widget }) {
  const { type, params = {} } = widget;

  const previewBox = {
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: 20,
    color: 'var(--text)',
  };

  if (type === 'banner') {
    return (
      <div style={{ ...previewBox, textAlign: 'center', fontSize: 15 }}>
        {params.emoji && <span style={{ marginRight: 8, fontSize: 20 }}>{params.emoji}</span>}
        {params.text}
      </div>
    );
  }

  if (type === 'hero_image') {
    return (
      <div style={{
        ...previewBox,
        backgroundImage: params.image_url ? `url(${params.image_url})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        minHeight: 120,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
      }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{params.title}</div>
        {params.button_text && (
          <span style={{ marginTop: 8, fontSize: 13, color: '#6366f1', fontWeight: 600 }}>
            {params.button_text} →
          </span>
        )}
      </div>
    );
  }

  if (type === 'promotional') {
    return (
      <div style={previewBox}>
        {params.badge_text && <span style={styles.previewBadge}>{params.badge_text}</span>}
        <div style={{ fontSize: 16, fontWeight: 700, marginTop: 8 }}>{params.title}</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{params.description}</div>
      </div>
    );
  }

  if (type === 'countdown_banner') {
    return (
      <div style={{ ...previewBox, textAlign: 'center' }}>
        <div style={{ fontSize: 15, fontWeight: 600 }}>{params.title}</div>
        <div style={{ fontSize: 24, fontWeight: 800, color: '#6366f1', margin: '8px 0' }}>00:00:00</div>
        {params.button_text && <span style={{ fontSize: 13, color: '#818cf8' }}>{params.button_text}</span>}
      </div>
    );
  }

  if (type === 'rating') {
    return (
      <div style={{ ...previewBox, textAlign: 'center' }}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{params.title}</div>
        <div style={{ fontSize: 28, margin: '8px 0', letterSpacing: 4 }}>
          {'★'.repeat(params.max_stars || 5)}
        </div>
        {params.subtitle && <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{params.subtitle}</div>}
      </div>
    );
  }

  if (type === 'poll') {
    return (
      <div style={previewBox}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>{params.question}</div>
        {(params.options || []).map((opt, i) => (
          <div key={i} style={{
            padding: '8px 12px',
            marginBottom: 6,
            border: '1px solid var(--border)',
            borderRadius: 6,
            fontSize: 13,
            cursor: 'pointer',
          }}>
            {typeof opt === 'string' ? opt : opt.label || opt.text || JSON.stringify(opt)}
          </div>
        ))}
      </div>
    );
  }

  if (type === 'progress') {
    const pct = params.progress || 0;
    return (
      <div style={previewBox}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{params.title}</div>
        <div style={{ height: 8, borderRadius: 4, background: '#27272a', marginTop: 10, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: '#6366f1', borderRadius: 4 }} />
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
          {params.progress_label || `${pct}%`}
        </div>
      </div>
    );
  }

  // Fallback: generic card
  return (
    <div style={previewBox}>
      {params.title && <div style={{ fontSize: 15, fontWeight: 600 }}>{params.title}</div>}
      {params.subtitle && <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{params.subtitle}</div>}
      {params.description && <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{params.description}</div>}
      {params.message && <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{params.message}</div>}
      {params.content && <div style={{ fontSize: 13, marginTop: 4 }}>{params.content}</div>}
      {params.text && <div style={{ fontSize: 14, marginTop: 4 }}>{params.text}</div>}
      {params.action_text && (
        <span style={{ fontSize: 13, color: '#6366f1', fontWeight: 600, marginTop: 8, display: 'inline-block' }}>
          {params.action_text} →
        </span>
      )}
    </div>
  );
}

/* ── Save-as-task mini component ─────────────────────────────────── */

function SaveAsTask({ prompt, apiKey }) {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          task: prompt,
          name: name.trim() || 'Widget Studio Task',
        }),
      });
      if (res.ok) setSaved(true);
    } catch {
      /* ignore – best effort */
    } finally {
      setSaving(false);
    }
  };

  if (saved) {
    return <div style={{ color: 'var(--success)', fontSize: 14, fontWeight: 600 }}>Saved! Go to Agent Tasks to manage it.</div>;
  }

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <input
        type="text"
        placeholder="Task name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        style={{ ...styles.input, flex: 1, marginBottom: 0 }}
      />
      <button onClick={handleSave} disabled={saving} style={styles.btnPrimary}>
        {saving ? 'Saving...' : 'Save'}
      </button>
    </div>
  );
}

/* ── Styles ──────────────────────────────────────────────────────── */

const styles = {
  tabs: {
    display: 'flex',
    gap: 0,
    marginBottom: 24,
    borderBottom: '1px solid var(--border)',
  },
  tab: {
    padding: '12px 20px',
    fontSize: 14,
    fontWeight: 600,
    background: 'none',
    border: 'none',
    borderBottom: '2px solid transparent',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  tabBadge: {
    fontSize: 11,
    fontWeight: 700,
    color: '#fff',
    background: '#6366f1',
    padding: '1px 7px',
    borderRadius: 10,
  },
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
  },
  catalogGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: 12,
  },
  widgetCard: {
    position: 'relative',
    textAlign: 'left',
    padding: 16,
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    cursor: 'pointer',
    transition: 'border-color 0.15s, background 0.15s',
  },
  widgetIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  checkMark: {
    position: 'absolute',
    top: 10,
    right: 10,
    width: 22,
    height: 22,
    borderRadius: '50%',
    background: '#6366f1',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: 700,
  },
  input: {
    width: '100%',
    padding: '10px 14px',
    fontSize: 14,
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text)',
    marginBottom: 12,
    outline: 'none',
  },
  textarea: {
    width: '100%',
    padding: '14px 16px',
    fontSize: 14,
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text)',
    marginBottom: 16,
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    lineHeight: 1.6,
  },
  templateChip: {
    padding: '6px 12px',
    fontSize: 12,
    color: 'var(--text-muted)',
    background: 'rgba(99,102,241,0.08)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: 20,
    cursor: 'pointer',
    textAlign: 'left',
  },
  selectionSummary: {
    padding: 12,
    background: 'rgba(99,102,241,0.06)',
    border: '1px solid rgba(99,102,241,0.15)',
    borderRadius: 8,
  },
  selectedChip: {
    fontSize: 12,
    padding: '3px 10px',
    background: 'var(--primary-muted)',
    color: '#818cf8',
    borderRadius: 14,
    fontWeight: 500,
  },
  btnPrimary: {
    padding: '10px 24px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#6366f1',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
  },
  btnGhost: {
    padding: '8px 16px',
    fontSize: 13,
    fontWeight: 500,
    color: 'var(--text-muted)',
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 8,
    cursor: 'pointer',
  },
  errorBanner: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 16px',
    marginBottom: 16,
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 8,
    color: '#ef4444',
    fontSize: 14,
  },
  errorClose: {
    background: 'none',
    border: 'none',
    color: '#ef4444',
    fontWeight: 700,
    fontSize: 16,
    cursor: 'pointer',
  },
  previewCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 20,
  },
  previewHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  previewIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    background: 'var(--primary-muted)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 20,
  },
  previewBody: {},
  previewBadge: {
    fontSize: 11,
    fontWeight: 700,
    color: '#f59e0b',
    background: 'rgba(245,158,11,0.15)',
    padding: '3px 10px',
    borderRadius: 12,
  },
  priorityBadge: {
    fontSize: 11,
    fontWeight: 700,
    color: '#6366f1',
    background: 'var(--primary-muted)',
    padding: '2px 8px',
    borderRadius: 10,
  },
  codeBlock: {
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    padding: '14px 18px',
    fontSize: 12,
    lineHeight: 1.6,
    color: '#c4b5fd',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    overflow: 'auto',
    whiteSpace: 'pre',
    margin: 0,
    marginTop: 8,
  },
  rawToggle: {
    fontSize: 14,
    color: 'var(--text-muted)',
    cursor: 'pointer',
  },
};
