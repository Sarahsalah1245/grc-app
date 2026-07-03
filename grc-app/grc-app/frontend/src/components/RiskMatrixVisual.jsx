const LEVEL_COLOR = {
  Low: '#3fb87f',
  Medium: '#e5c93d',
  High: '#e5793d',
  Critical: '#e5473d',
};

// Mirrors the backend logic (RISK_MATRIX_LABELS) - duplicated here just for instant visual feedback without an API call
const MATRIX = {
  '1,1': 'Low', '1,2': 'Low', '1,3': 'Low', '1,4': 'Medium', '1,5': 'Medium',
  '2,1': 'Low', '2,2': 'Low', '2,3': 'Medium', '2,4': 'Medium', '2,5': 'High',
  '3,1': 'Low', '3,2': 'Medium', '3,3': 'Medium', '3,4': 'High', '3,5': 'High',
  '4,1': 'Medium', '4,2': 'Medium', '4,3': 'High', '4,4': 'High', '4,5': 'Critical',
  '5,1': 'Medium', '5,2': 'High', '5,3': 'High', '5,4': 'Critical', '5,5': 'Critical',
};

export default function RiskMatrixVisual({ likelihood, impact }) {
  const rows = [5, 4, 3, 2, 1];
  const cols = [1, 2, 3, 4, 5];

  return (
    <div>
      <div className="matrix-grid">
        {rows.map(l => cols.map(i => {
          const level = MATRIX[`${l},${i}`];
          const isSelected = l === likelihood && i === impact;
          return (
            <div
              key={`${l}-${i}`}
              className={'matrix-cell' + (isSelected ? ' selected' : '')}
              style={{ background: LEVEL_COLOR[level] }}
              title={`Likelihood ${l} x Impact ${i} = ${level}`}
            >
              {l * i}
            </div>
          );
        }))}
      </div>
      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 8 }}>
        Row = Likelihood (bottom to top) &middot; Column = Impact severity (left to right)
      </p>
    </div>
  );
}
