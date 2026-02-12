import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

const EXAMPLE_TASKS = [
  'Benim appim bir kiyafet uygulamasi, kullaniciya hava durumuna gore oneri kombinler gosteren widget goster',
  'Benim appim bir diyet uygulamasi, kullaniciya mevsime gore meyveler oneren widget gostermeli',
  'Benim appim bir fitness uygulamasi, kullaniciya gunluk motivasyon mesajlari ve ilerleme gostersin',
  'Benim appim bir e-ticaret uygulamasi, ozel gunlerde kampanya banner\'lari ve indirim widget\'lari gostersin',
  'Benim appim bir seyahat uygulamasi, gidilecek yerin hava durumuna gore packing onerileri gostersin',
];

export default function AgentTasks() {
  const apiKey = localStorage.getItem('intyx_api_key');
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [taskName, setTaskName] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!apiKey) return;
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks?api_key=${encodeURIComponent(apiKey)}`);
      if (!res.ok) throw new Error('Gorevler yuklenemedi');
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      // Fallback to localStorage
      try {
        const saved = localStorage.getItem('intyx_agent_tasks');
        if (saved) setTasks(JSON.parse(saved));
      } catch (_) { /* ignore parse errors */ }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newTask.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          task: newTask.trim(),
          name: taskName.trim() || 'Gorev',
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Gorev olusturulamadi');
      }
      setNewTask('');
      setTaskName('');
      await fetchTasks();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/agent-tasks/${id}?api_key=${encodeURIComponent(apiKey)}`,
        { method: 'DELETE' }
      );
      if (!res.ok) throw new Error('Silinemedi');
      setTasks(tasks.filter((t) => t.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggle = async (id) => {
    const task = tasks.find((t) => t.id === id);
    if (!task) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, active: !task.active }),
      });
      if (!res.ok) throw new Error('Guncellenemedi');
      setTasks(tasks.map((t) => (t.id === id ? { ...t, active: !t.active } : t)));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleTest = async (task) => {
    setTesting(task.id);
    setTestResult(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent-tasks/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          task_id: task.id,
          context: { current_date: new Date().toISOString() },
        }),
      });
      if (!res.ok) throw new Error('Test basarisiz');
      const data = await res.json();
      setTestResult({ taskId: task.id, widgets: data.widgets || [] });
    } catch (err) {
      setTestResult({
        taskId: task.id,
        widgets: [],
        error: err.message,
      });
    } finally {
      setTesting(null);
    }
  };

  if (!apiKey) {
    return (
      <div style={{ maxWidth: 600, margin: '0 auto', padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 24 }}>🤖</div>
        <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>Once paket alin</h2>
        <p style={{ color: 'var(--text-muted)' }}>Agent gorevleri tanimlamak icin bir paket secmeniz gerekiyor.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Agent Gorevleri</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
        Uygulamanizi tanimlayin, AI agent bu goreve gore hangi widget'lari gosterecegine karar versin.
      </p>

      {error && (
        <div style={styles.errorBanner}>
          {error}
          <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', color: '#ef4444', fontWeight: 700, marginLeft: 12 }}>✕</button>
        </div>
      )}

      {/* Create new task */}
      <div style={styles.card}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Yeni Gorev Tanimla</h3>
        <input
          type="text"
          placeholder="Gorev adi (orn: Hava Durumu Onerileri)"
          value={taskName}
          onChange={(e) => setTaskName(e.target.value)}
          style={styles.input}
        />
        <textarea
          placeholder="Uygulamanizi ve ne yapmak istediginizi detayli anlatın...&#10;&#10;Ornek: Benim appim bir kiyafet uygulamasi, kullaniciya hava durumuna gore oneri kombinler gosteren widget goster"
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          style={styles.textarea}
          rows={4}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button onClick={handleCreate} disabled={!newTask.trim() || saving} style={styles.btnPrimary}>
            {saving ? 'Kaydediliyor...' : 'Gorevi Kaydet'}
          </button>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Bu metin AI agent'a kisilik olarak verilir
          </span>
        </div>
      </div>

      {/* Example tasks */}
      <div style={{ ...styles.card, marginTop: 16 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>
          Ornek Gorev Tanimlari
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {EXAMPLE_TASKS.map((ex, i) => (
            <button
              key={i}
              onClick={() => setNewTask(ex)}
              style={styles.exampleChip}
            >
              {ex.length > 60 ? ex.slice(0, 60) + '...' : ex}
            </button>
          ))}
        </div>
      </div>

      {/* Task list */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Yukleniyor...</div>
      ) : tasks.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Kayitli Gorevler</h2>
          {tasks.map((task) => (
            <div key={task.id} style={{ ...styles.card, marginBottom: 12, opacity: task.active ? 1 : 0.5 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <h4 style={{ fontSize: 15, fontWeight: 600 }}>{task.name}</h4>
                    <span style={{
                      fontSize: 11,
                      padding: '2px 8px',
                      borderRadius: 10,
                      background: task.active ? 'var(--success-muted)' : 'rgba(161,161,170,0.15)',
                      color: task.active ? 'var(--success)' : 'var(--text-muted)',
                      fontWeight: 600,
                    }}>
                      {task.active ? 'Aktif' : 'Pasif'}
                    </span>
                  </div>
                  <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.5 }}>{task.task}</p>
                  <code style={{ fontSize: 12, marginTop: 8, display: 'inline-block' }}>{task.id}</code>
                </div>
                <div style={{ display: 'flex', gap: 8, marginLeft: 16, flexShrink: 0 }}>
                  <button onClick={() => handleTest(task)} disabled={testing !== null} style={styles.btnSmall}>
                    {testing === task.id ? '...' : '▶ Test'}
                  </button>
                  <button onClick={() => handleToggle(task.id)} style={styles.btnSmall}>
                    {task.active ? '⏸' : '▶'}
                  </button>
                  <button onClick={() => handleDelete(task.id)} style={{ ...styles.btnSmall, color: '#ef4444' }}>
                    ✕
                  </button>
                </div>
              </div>

              {/* Test result */}
              {testResult && testResult.taskId === task.id && (
                <div style={styles.testResult}>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                    AI Agent Ciktisi {testResult.error ? '(Hata)' : ''}
                  </div>
                  {testResult.error ? (
                    <p style={{ color: '#ef4444', fontSize: 13 }}>{testResult.error}</p>
                  ) : (
                    <pre style={styles.codeBlock}>
                      {JSON.stringify(testResult.widgets, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Integration code */}
      {tasks.length > 0 && (
        <div style={{ ...styles.card, marginTop: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Flutter Entegrasyonu</h3>
          <pre style={styles.codeBlock}>{`// Agent'a gorev ile widget iste
final response = await widgetService.resolveAgentTask(
  taskId: '${tasks[0]?.id ?? 'task_xxx'}',
  context: {
    'weather': currentWeather,
    'user_preferences': userPrefs,
    'current_date': DateTime.now().toIso8601String(),
  },
);

// Widget'lari goster
DynamicWidgetContainer(
  responseJson: response,
  colorScheme: Theme.of(context).colorScheme,
)`}</pre>
        </div>
      )}

      <div style={{ height: 80 }} />
    </div>
  );
}

const styles = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
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
    padding: '12px 14px',
    fontSize: 14,
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text)',
    marginBottom: 16,
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    lineHeight: 1.5,
  },
  btnPrimary: {
    padding: '10px 24px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#6366f1',
    border: 'none',
    borderRadius: 8,
  },
  btnSmall: {
    padding: '6px 12px',
    fontSize: 13,
    fontWeight: 500,
    color: 'var(--text-muted)',
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 6,
  },
  exampleChip: {
    padding: '6px 12px',
    fontSize: 12,
    color: 'var(--text-muted)',
    background: 'rgba(99,102,241,0.08)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: 20,
    cursor: 'pointer',
    textAlign: 'left',
  },
  testResult: {
    marginTop: 16,
    padding: 16,
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
  },
  codeBlock: {
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    padding: '14px 18px',
    fontSize: 13,
    lineHeight: 1.6,
    color: '#c4b5fd',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    overflow: 'auto',
    whiteSpace: 'pre',
    margin: 0,
  },
};
