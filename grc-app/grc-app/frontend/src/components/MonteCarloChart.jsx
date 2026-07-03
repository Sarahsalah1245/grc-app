import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function MonteCarloChart({ result }) {
  if (!result) return null;

  const { counts, bin_edges } = result.histogram;
  const data = counts.map((count, i) => ({
    range: `${Math.round(bin_edges[i] / 1000)}k`,
    count,
    mid: (bin_edges[i] + bin_edges[i + 1]) / 2,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <XAxis dataKey="range" tick={{ fill: '#8aa0c2', fontSize: 11 }} />
          <YAxis tick={{ fill: '#8aa0c2', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: '#16233a', border: '1px solid #253652', borderRadius: 8 }}
            labelStyle={{ color: '#e8edf5' }}
            formatter={(value) => [value, 'Scenario count']}
          />
          <Bar dataKey="count" fill="#e5a13d" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      <div className="grid-2" style={{ marginTop: 10 }}>
        <div>
          <div className="metric-label">Value at Risk (VaR 95%)</div>
          <div className="metric">{result.value_at_risk_95.toLocaleString()}</div>
        </div>
        <div>
          <div className="metric-label">Mean Annual Loss</div>
          <div className="metric">{result.mean_annual_loss.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
}
