import { useState } from 'react';
import { api } from '../lib/api';

const CATEGORY_LABELS = {
  strength: 'Strength',
  weakness: 'Weakness',
  opportunity: 'Opportunity',
  threat: 'Threat',
};

export default function SwotAnalysis() {
  const [entries, setEntries] = useState([
    { category: 'threat', description: '', weight: 3 },
  ]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function updateEntry(idx, field, value) {
    setEntries(prev => prev.map((e, i) => i === idx ? { ...e, [field]: value } : e));
  }

  function addEntry(category) {
    setEntries(prev => [...prev, { category, description: '', weight: 3 }]);
  }

  function removeEntry(idx) {
    setEntries(prev => prev.filter((_, i) => i !== idx));
  }

  async function handleAnalyze() {
    setError(''); setLoading(true);
    try {
      const valid = entries.filter(e => e.description.trim().length > 0)
        .map(e => ({ ...e, weight: Number(e.weight) }));
      if (valid.length === 0) throw new Error('Add at least one entry with a description');
      const res = await api.swotAnalyze(valid);
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div>
      <h1>SWOT Analysis</h1>
      <p className="subtitle">Add strengths, weaknesses, opportunities, and threats, and we'll show you the strategic posture and top risk candidates</p>

      <div className="card">
        {entries.map((entry, idx) => (
          <div key={idx} className="grid-2" style={{ marginBottom: 12, alignItems: 'end' }}>
            <div>
              <label>{idx === 0 ? 'Category' : ''}</label>
              <select value={entry.category} onChange={e => updateEntry(idx, 'category', e.target.value)}>
                {Object.entries(CATEGORY_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ flex: 1 }}>
                <label>{idx === 0 ? 'Description' : ''}</label>
                <input value={entry.description} onChange={e => updateEntry(idx, 'description', e.target.value)} placeholder="e.g. No regular data backups" />
              </div>
              <div style={{ width: 70 }}>
                <label>{idx === 0 ? 'Weight' : ''}</label>
                <input type="number" min="1" max="5" value={entry.weight} onChange={e => updateEntry(idx, 'weight', e.target.value)} />
              </div>
              <button className="ghost" style={{ marginTop: idx === 0 ? 22 : 0 }} onClick={() => removeEntry(idx)}>Remove</button>
            </div>
          </div>
        ))}

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10 }}>
          {Object.entries(CATEGORY_LABELS).map(([val, label]) => (
            <button key={val} className="ghost" onClick={() => addEntry(val)}>+ {label}</button>
          ))}
        </div>

        <button className="primary" onClick={handleAnalyze} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze SWOT'}
        </button>
        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <div className="card">
          <h2>Strategic Posture</h2>
          <p style={{ fontSize: '1rem' }}>{result.strategic_posture}</p>

          <div className="grid-2">
            <div>
              <div className="metric-label">Internal balance (strength - weakness)</div>
              <div className="metric">{result.internal_balance}</div>
            </div>
            <div>
              <div className="metric-label">External balance (opportunity - threat)</div>
              <div className="metric">{result.external_balance}</div>
            </div>
          </div>

          {result.suggested_risk_candidates.length > 0 && (
            <div style={{ marginTop: 18 }}>
              <h2 style={{ fontSize: '0.95rem' }}>Candidates for Formal Risk Items</h2>
              {result.suggested_risk_candidates.map((c, i) => (
                <div key={i} style={{ fontSize: '0.88rem', marginBottom: 6 }}>
                  <span className="badge badge-High" style={{ marginInlineEnd: 8 }}>{CATEGORY_LABELS[c.category]}</span>
                  {c.description} (weight: {c.weight})
                </div>
              ))}
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 10 }}>
                💡 Head to "Risk Calculator" → "Full Analysis" and use these as your threat description to turn them into a complete, COBIT-mapped risk assessment.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
