import React from 'react';

/**
 * 5×5 Risk Matrix component.
 * Rows = Consequence (5 at top, 1 at bottom)
 * Cols = Likelihood (1 at left, 5 at right)
 *
 * Color rules (likelihood × consequence):
 *   1-4  → low
 *   5-9  → medium
 *   10-16 → high
 *   17-25 → critical
 */

function getCellLevel(likelihood, consequence) {
  const score = likelihood * consequence;
  if (score >= 17) return 'critical';
  if (score >= 10) return 'high';
  if (score >= 5) return 'medium';
  return 'low';
}

export default function RiskMatrix({ riskMatrix }) {
  // Build a lookup: "likelihood-consequence" -> [risk_ids]
  const cellMap = {};
  (riskMatrix || []).forEach((r) => {
    const key = `${r.likelihood}-${r.consequence}`;
    if (!cellMap[key]) cellMap[key] = [];
    cellMap[key].push(r.risk_id);
  });

  const rows = [5, 4, 3, 2, 1]; // consequence top-down
  const cols = [1, 2, 3, 4, 5]; // likelihood left-right

  return (
    <div className="risk-matrix glass-card">
      <div className="risk-matrix__title">
        📊 Matriz de Riesgos (Probabilidad × Consecuencia)
      </div>

      <div className="risk-matrix__grid" style={{
        display: 'grid',
        gridTemplateColumns: '28px repeat(5, 1fr)',
        gridTemplateRows: 'repeat(5, 1fr) 28px',
        gap: '3px',
      }}>
        {rows.map((consequence, rowIdx) => (
          <React.Fragment key={`row-${consequence}`}>
            {/* Y-axis label */}
            <div className="risk-matrix__ylabel" style={{
              gridColumn: 1,
              gridRow: rowIdx + 1,
              fontSize: '0.65rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              {consequence}
            </div>

            {/* Cells */}
            {cols.map((likelihood) => {
              const level = getCellLevel(likelihood, consequence);
              const key = `${likelihood}-${consequence}`;
              const risks = cellMap[key] || [];
              const hasRisk = risks.length > 0;

              return (
                <div
                  key={key}
                  className={`risk-matrix__cell risk-matrix__cell--${level} ${hasRisk ? 'risk-matrix__cell--has-risk' : ''}`}
                  title={hasRisk ? risks.join(', ') : `P:${likelihood} × C:${consequence}`}
                >
                  {hasRisk ? risks.join('\n') : ''}
                </div>
              );
            })}
          </React.Fragment>
        ))}

        {/* X-axis labels */}
        <div style={{ gridColumn: 1 }}></div>
        {cols.map((l) => (
          <div key={`xlabel-${l}`} className="risk-matrix__xlabel">
            {l}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
        <span className="risk-matrix__axis-label" style={{ fontSize: '0.65rem' }}>
          ↑ Consecuencia
        </span>
        <span className="risk-matrix__axis-label" style={{ fontSize: '0.65rem' }}>
          Probabilidad →
        </span>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex', gap: '0.75rem', marginTop: '0.75rem',
        justifyContent: 'center', flexWrap: 'wrap',
      }}>
        {[
          { level: 'low', label: 'Bajo' },
          { level: 'medium', label: 'Medio' },
          { level: 'high', label: 'Alto' },
          { level: 'critical', label: 'Crítico' },
        ].map(({ level, label }) => (
          <div key={level} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <div
              className={`risk-matrix__cell--${level}`}
              style={{ width: 12, height: 12, borderRadius: 3 }}
            ></div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
