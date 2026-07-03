import { useState } from 'react';
import { api } from '../lib/api';
import RiskMatrixVisual from '../components/RiskMatrixVisual';
import MonteCarloChart from '../components/MonteCarloChart';

const TABS = [
  { id: 'qualitative', label: 'Qualitative' },
  { id: 'quantitative', label: 'Quantitative (ALE)' },
  { id: 'montecarlo', label: 'Monte Carlo' },
  { id: 'fmea', label: 'FMEA' },
  { id: 'bowtie', label: 'Bow-Tie' },
  { id: 'full', label: 'Full Analysis + COBIT' },
];

function ErrorBox({ error }) {
  if (!error) return null;
  return <div className="error-box">{error}</div>;
}

function QualitativeTab() {
  const [likelihood, setLikelihood] = useState(3);
  const [impact, setImpact] = useState(3);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const res = await api.qualitative({ likelihood: Number(likelihood), impact: Number(impact) });
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div className="grid-2">
      <div className="card">
        <h2>Qualitative Assessment Inputs</h2>
        <label>Likelihood of occurrence (1 rare - 5 almost certain)</label>
        <input type="range" min="1" max="5" value={likelihood} onChange={e => setLikelihood(e.target.value)} />
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>{likelihood}/5</div>

        <label>Impact severity (1 minor - 5 catastrophic)</label>
        <input type="range" min="1" max="5" value={impact} onChange={e => setImpact(e.target.value)} />
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>{impact}/5</div>

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Risk Level'}
        </button>
        <ErrorBox error={error} />
      </div>

      <div className="card">
        <h2>Risk Matrix</h2>
        <RiskMatrixVisual likelihood={Number(likelihood)} impact={Number(impact)} />
        {result && (
          <div style={{ marginTop: 20 }}>
            <span className={`badge badge-${result.risk_level}`}>{result.risk_level}</span>
            <span style={{ marginInlineStart: 10, color: 'var(--text-muted)' }}>
              Risk score: {result.risk_score}/25
            </span>
            {result.ai_explanation && <div className="ai-box">{result.ai_explanation}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

function QuantitativeTab() {
  const [form, setForm] = useState({ asset_value: 1000000, exposure_factor: 0.4, aro: 0.5 });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function update(k, v) { setForm(prev => ({ ...prev, [k]: v })); }

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const res = await api.quantitative({
        asset_value: Number(form.asset_value),
        exposure_factor: Number(form.exposure_factor),
        aro: Number(form.aro),
      });
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div className="grid-2">
      <div className="card">
        <h2>Quantitative Assessment Inputs (ALE)</h2>
        <label>Asset Value</label>
        <input type="number" value={form.asset_value} onChange={e => update('asset_value', e.target.value)} />

        <label>Exposure Factor (0 - 1)</label>
        <input type="number" step="0.05" min="0" max="1" value={form.exposure_factor} onChange={e => update('exposure_factor', e.target.value)} />

        <label>Annual Rate of Occurrence - ARO (e.g. 0.5 = once every 2 years)</label>
        <input type="number" step="0.1" min="0" value={form.aro} onChange={e => update('aro', e.target.value)} />

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Annual Loss'}
        </button>
        <ErrorBox error={error} />
      </div>

      {result && (
        <div className="card">
          <h2>Result</h2>
          <div className="grid-2">
            <div>
              <div className="metric-label">SLE (Single Loss Expectancy)</div>
              <div className="metric">{result.sle.toLocaleString()}</div>
            </div>
            <div>
              <div className="metric-label">ALE (Annual Loss Expectancy)</div>
              <div className="metric" style={{ color: 'var(--accent-amber)' }}>{result.ale.toLocaleString()}</div>
            </div>
          </div>
          {result.ai_explanation && <div className="ai-box">{result.ai_explanation}</div>}
        </div>
      )}
    </div>
  );
}

function MonteCarloTab() {
  const [form, setForm] = useState({
    freq_min: 1, freq_most_likely: 3, freq_max: 6,
    mag_min: 20000, mag_most_likely: 80000, mag_max: 300000,
    iterations: 10000,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function update(k, v) { setForm(prev => ({ ...prev, [k]: v })); }

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([k, v]) => [k, Number(v)]));
      const res = await api.monteCarlo(payload);
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div>
      <div className="card">
        <h2>Monte Carlo Simulation (FAIR-style)</h2>
        <p className="subtitle" style={{ marginBottom: 10 }}>
          Instead of one fixed number, give a range (min - most likely - max) for frequency and loss magnitude, and we'll run thousands of scenarios.
        </p>
        <div className="grid-2">
          <div>
            <label>Occurrences per year - minimum</label>
            <input type="number" value={form.freq_min} onChange={e => update('freq_min', e.target.value)} />
            <label>Most likely</label>
            <input type="number" value={form.freq_most_likely} onChange={e => update('freq_most_likely', e.target.value)} />
            <label>Maximum</label>
            <input type="number" value={form.freq_max} onChange={e => update('freq_max', e.target.value)} />
          </div>
          <div>
            <label>Loss per event - minimum</label>
            <input type="number" value={form.mag_min} onChange={e => update('mag_min', e.target.value)} />
            <label>Most likely</label>
            <input type="number" value={form.mag_most_likely} onChange={e => update('mag_most_likely', e.target.value)} />
            <label>Maximum</label>
            <input type="number" value={form.mag_max} onChange={e => update('mag_max', e.target.value)} />
          </div>
        </div>

        <label>Number of scenarios (Iterations)</label>
        <input type="number" step="1000" min="1000" max="100000" value={form.iterations} onChange={e => update('iterations', e.target.value)} />

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Running simulation...' : 'Run Simulation'}
        </button>
        <ErrorBox error={error} />
      </div>

      {result && (
        <div className="card">
          <h2>Annual Loss Distribution</h2>
          <MonteCarloChart result={result} />
          {result.ai_explanation && <div className="ai-box">{result.ai_explanation}</div>}
        </div>
      )}
    </div>
  );
}

function FmeaTab() {
  const [form, setForm] = useState({ severity: 5, occurrence: 5, detection: 5 });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function update(k, v) { setForm(prev => ({ ...prev, [k]: v })); }

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const res = await api.fmea({
        severity: Number(form.severity),
        occurrence: Number(form.occurrence),
        detection: Number(form.detection),
      });
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div className="grid-2">
      <div className="card">
        <h2>FMEA Inputs</h2>
        <p className="subtitle" style={{ marginBottom: 10 }}>
          Failure Mode and Effects Analysis - great for ranking many possible failures by priority.
        </p>
        <label>Severity (1 negligible - 10 catastrophic)</label>
        <input type="range" min="1" max="10" value={form.severity} onChange={e => update('severity', e.target.value)} />
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>{form.severity}/10</div>

        <label>Occurrence (1 very unlikely - 10 almost certain)</label>
        <input type="range" min="1" max="10" value={form.occurrence} onChange={e => update('occurrence', e.target.value)} />
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>{form.occurrence}/10</div>

        <label>Detection (1 you'll definitely catch it early - 10 you'll almost never catch it in time)</label>
        <input type="range" min="1" max="10" value={form.detection} onChange={e => update('detection', e.target.value)} />
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>{form.detection}/10</div>

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate RPN'}
        </button>
        <ErrorBox error={error} />
      </div>

      {result && (
        <div className="card">
          <h2>Result</h2>
          <span className={`badge badge-${result.risk_level}`}>{result.risk_level}</span>
          <div style={{ marginTop: 14 }}>
            <div className="metric-label">Risk Priority Number (RPN)</div>
            <div className="metric">{result.rpn} / 1000</div>
          </div>
          {result.ai_explanation && <div className="ai-box">{result.ai_explanation}</div>}
        </div>
      )}
    </div>
  );
}

function BowtieTab() {
  const [topEvent, setTopEvent] = useState('');
  const [threats, setThreats] = useState([{ description: '', preventive_controls: [{ name: '', effectiveness: 3 }] }]);
  const [consequences, setConsequences] = useState([{ description: '', severity: 3, mitigating_controls: [{ name: '', effectiveness: 3 }] }]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function updateThreat(i, field, value) {
    setThreats(prev => prev.map((t, idx) => idx === i ? { ...t, [field]: value } : t));
  }
  function updateThreatControl(i, field, value) {
    setThreats(prev => prev.map((t, idx) => idx === i ? { ...t, preventive_controls: [{ ...t.preventive_controls[0], [field]: value }] } : t));
  }
  function updateConsequence(i, field, value) {
    setConsequences(prev => prev.map((c, idx) => idx === i ? { ...c, [field]: value } : c));
  }
  function updateConsequenceControl(i, field, value) {
    setConsequences(prev => prev.map((c, idx) => idx === i ? { ...c, mitigating_controls: [{ ...c.mitigating_controls[0], [field]: value }] } : c));
  }

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const payload = {
        top_event: topEvent,
        threats: threats.map(t => ({ ...t, preventive_controls: t.preventive_controls.map(c => ({ ...c, effectiveness: Number(c.effectiveness) })) })),
        consequences: consequences.map(c => ({ ...c, severity: Number(c.severity), mitigating_controls: c.mitigating_controls.map(m => ({ ...m, effectiveness: Number(m.effectiveness) })) })),
      };
      const res = await api.bowtie(payload);
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div>
      <div className="card">
        <h2>Bow-Tie Analysis</h2>
        <p className="subtitle" style={{ marginBottom: 10 }}>
          Map one central risk event to its causes (with preventive controls) and consequences (with mitigating controls).
        </p>

        <label>Top Event (the central hazard)</label>
        <input value={topEvent} onChange={e => setTopEvent(e.target.value)} placeholder="e.g. Customer database breach" />

        <h2 style={{ fontSize: '0.95rem', marginTop: 20 }}>Threat (Cause) &amp; Preventive Control</h2>
        {threats.map((t, i) => (
          <div key={i} className="grid-2" style={{ marginBottom: 10 }}>
            <div>
              <label>Threat description</label>
              <input value={t.description} onChange={e => updateThreat(i, 'description', e.target.value)} placeholder="e.g. Weak employee passwords" />
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ flex: 1 }}>
                <label>Preventive control</label>
                <input value={t.preventive_controls[0].name} onChange={e => updateThreatControl(i, 'name', e.target.value)} placeholder="e.g. MFA" />
              </div>
              <div style={{ width: 70 }}>
                <label>Effect. (1-5)</label>
                <input type="number" min="1" max="5" value={t.preventive_controls[0].effectiveness} onChange={e => updateThreatControl(i, 'effectiveness', e.target.value)} />
              </div>
            </div>
          </div>
        ))}

        <h2 style={{ fontSize: '0.95rem', marginTop: 20 }}>Consequence &amp; Mitigating Control</h2>
        {consequences.map((c, i) => (
          <div key={i} className="grid-2" style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ flex: 1 }}>
                <label>Consequence description</label>
                <input value={c.description} onChange={e => updateConsequence(i, 'description', e.target.value)} placeholder="e.g. Customer data leak" />
              </div>
              <div style={{ width: 70 }}>
                <label>Severity (1-5)</label>
                <input type="number" min="1" max="5" value={c.severity} onChange={e => updateConsequence(i, 'severity', e.target.value)} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ flex: 1 }}>
                <label>Mitigating control</label>
                <input value={c.mitigating_controls[0].name} onChange={e => updateConsequenceControl(i, 'name', e.target.value)} placeholder="e.g. Incident response plan" />
              </div>
              <div style={{ width: 70 }}>
                <label>Effect. (1-5)</label>
                <input type="number" min="1" max="5" value={c.mitigating_controls[0].effectiveness} onChange={e => updateConsequenceControl(i, 'effectiveness', e.target.value)} />
              </div>
            </div>
          </div>
        ))}

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Bow-Tie Analysis'}
        </button>
        <ErrorBox error={error} />
      </div>

      {result && (
        <div className="card">
          <h2>{result.top_event}</h2>
          <p style={{ fontSize: '0.95rem' }}>{result.barrier_health}</p>
          <div className="grid-2">
            <div>
              <div className="metric-label">Avg. preventive control effectiveness</div>
              <div className="metric">{result.average_preventive_effectiveness}/5</div>
            </div>
            <div>
              <div className="metric-label">Overall residual severity</div>
              <div className="metric" style={{ color: 'var(--accent-amber)' }}>{result.overall_residual_severity}</div>
            </div>
          </div>
          {result.ai_explanation && <div className="ai-box">{result.ai_explanation}</div>}
        </div>
      )}
    </div>
  );
}

function FullAnalysisTab() {
  const [form, setForm] = useState({
    asset_name: '', threat_description: '',
    likelihood: 3, impact: 3,
    asset_value: 1000000, exposure_factor: 0.4, aro: 0.5,
  });
  const [includeMonteCarlo, setIncludeMonteCarlo] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function update(k, v) { setForm(prev => ({ ...prev, [k]: v })); }

  async function handleCalc() {
    setError(''); setLoading(true);
    try {
      const payload = {
        asset_name: form.asset_name,
        threat_description: form.threat_description,
        qualitative: { likelihood: Number(form.likelihood), impact: Number(form.impact) },
        quantitative: {
          asset_value: Number(form.asset_value),
          exposure_factor: Number(form.exposure_factor),
          aro: Number(form.aro),
        },
        monte_carlo: includeMonteCarlo ? {
          freq_min: 1, freq_most_likely: Number(form.aro) * 2 || 1, freq_max: (Number(form.aro) * 2 || 1) + 3,
          mag_min: Number(form.asset_value) * Number(form.exposure_factor) * 0.5,
          mag_most_likely: Number(form.asset_value) * Number(form.exposure_factor),
          mag_max: Number(form.asset_value) * Number(form.exposure_factor) * 1.8,
          iterations: 8000,
        } : null,
        generate_ai_explanation: true,
        map_to_cobit: true,
      };
      const res = await api.fullAnalysis(payload);
      setResult(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div>
      <div className="card">
        <h2>Full Analysis for One Risk</h2>
        <p className="subtitle" style={{ marginBottom: 10 }}>
          Combines qualitative + quantitative + (optional) Monte Carlo, and automatically maps the result to the right COBIT 2019 objectives.
        </p>

        <label>Asset name (e.g. Customer database)</label>
        <input value={form.asset_name} onChange={e => update('asset_name', e.target.value)} />

        <label>Threat description</label>
        <textarea value={form.threat_description} onChange={e => update('threat_description', e.target.value)} />

        <div className="grid-2">
          <div>
            <label>Likelihood (1-5)</label>
            <input type="number" min="1" max="5" value={form.likelihood} onChange={e => update('likelihood', e.target.value)} />
            <label>Impact (1-5)</label>
            <input type="number" min="1" max="5" value={form.impact} onChange={e => update('impact', e.target.value)} />
          </div>
          <div>
            <label>Asset value</label>
            <input type="number" value={form.asset_value} onChange={e => update('asset_value', e.target.value)} />
            <label>Exposure Factor (0-1)</label>
            <input type="number" step="0.05" value={form.exposure_factor} onChange={e => update('exposure_factor', e.target.value)} />
            <label>ARO</label>
            <input type="number" step="0.1" value={form.aro} onChange={e => update('aro', e.target.value)} />
          </div>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 16 }}>
          <input type="checkbox" style={{ width: 'auto' }} checked={includeMonteCarlo} onChange={e => setIncludeMonteCarlo(e.target.checked)} />
          Also run a Monte Carlo simulation automatically (based on the asset values above)
        </label>

        <button className="primary" onClick={handleCalc} disabled={loading}>
          {loading ? 'Analyzing (takes a few seconds because of the AI)...' : 'Run Full Analysis'}
        </button>
        <ErrorBox error={error} />
      </div>

      {result && (
        <div className="card">
          <h2>{result.asset_name}</h2>
          <div className="grid-2">
            <div>
              <span className={`badge badge-${result.qualitative.risk_level}`}>{result.qualitative.risk_level}</span>
              <div className="metric-label" style={{ marginTop: 10 }}>Annual Loss Expectancy (ALE)</div>
              <div className="metric">{result.quantitative.ale.toLocaleString()}</div>
            </div>
            {result.monte_carlo && (
              <div>
                <div className="metric-label">VaR 95% (Monte Carlo)</div>
                <div className="metric" style={{ color: 'var(--accent-amber)' }}>
                  {result.monte_carlo.value_at_risk_95.toLocaleString()}
                </div>
              </div>
            )}
          </div>

          {result.cobit_mapping && result.cobit_mapping.selected && (
            <div style={{ marginTop: 18 }}>
              <h2 style={{ fontSize: '0.95rem' }}>COBIT 2019 Mapping</h2>
              {result.cobit_mapping.selected.map(obj => (
                <div key={obj.id} style={{ marginBottom: 8, fontSize: '0.88rem' }}>
                  <span className="badge badge-Medium" style={{ marginInlineEnd: 8 }}>{obj.id}</span>
                  {obj.reason}
                </div>
              ))}
            </div>
          )}

          {result.ai_explanation && (
            <>
              <h2 style={{ fontSize: '0.95rem', marginTop: 18 }}>AI Explanation (XAI)</h2>
              <div className="ai-box">{result.ai_explanation.qualitative}</div>
              <div className="ai-box">{result.ai_explanation.quantitative}</div>
              {result.ai_explanation.monte_carlo && <div className="ai-box">{result.ai_explanation.monte_carlo}</div>}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default function RiskCalculator() {
  const [tab, setTab] = useState('qualitative');

  return (
    <div>
      <h1>Risk Calculator</h1>
      <p className="subtitle">Assess risks using six different methods, each with an automatic AI explanation</p>

      <div className="tabs">
        {TABS.map(t => (
          <button key={t.id} className={'tab-btn' + (tab === t.id ? ' active' : '')} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'qualitative' && <QualitativeTab />}
      {tab === 'quantitative' && <QuantitativeTab />}
      {tab === 'montecarlo' && <MonteCarloTab />}
      {tab === 'fmea' && <FmeaTab />}
      {tab === 'bowtie' && <BowtieTab />}
      {tab === 'full' && <FullAnalysisTab />}
    </div>
  );
}
