import { useEffect, useState } from 'react';
import { api } from '../lib/api';

export default function CobitReference() {
  const [objectives, setObjectives] = useState([]);
  const [description, setDescription] = useState('');
  const [mapping, setMapping] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.cobitObjectives().then(setObjectives).catch(() => {});
  }, []);

  async function handleMap() {
    setError(''); setLoading(true);
    try {
      const res = await api.cobitMap(description);
      setMapping(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div>
      <h1>COBIT 2019 Reference</h1>
      <p className="subtitle">Describe any risk or issue, and we'll tell you the most relevant COBIT 2019 governance/management objectives to address it</p>

      <div className="card">
        <label>Risk or issue description</label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="e.g. There is no monitoring for failed login attempts on the payment system"
        />
        <button className="primary" onClick={handleMap} disabled={loading || description.length < 5}>
          {loading ? 'Analyzing...' : 'Map to COBIT'}
        </button>
        {error && <div className="error-box">{error}</div>}

        {mapping && mapping.selected && (
          <div style={{ marginTop: 16 }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>{mapping.summary}</p>
            {mapping.selected.map(obj => (
              <div key={obj.id} className="ai-box" style={{ marginTop: 8 }}>
                <span className="badge badge-Medium" style={{ marginInlineEnd: 8 }}>{obj.id}</span>
                {obj.reason}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h2>All COBIT 2019 Objectives Available in the System</h2>
        {objectives.map(obj => (
          <div key={obj.id} style={{ padding: '10px 0', borderBottom: '1px solid var(--line)' }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'baseline' }}>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)', fontWeight: 700 }}>{obj.id}</span>
              <strong>{obj.title}</strong>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{obj.domain}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
