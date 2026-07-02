import React from 'react';

const STATUS_CONFIG = {
  ok:       { icon: '✅', label: 'Conforme', className: 'support-comparison__status--ok' },
  warning:  { icon: '⚠️', label: 'Alerta',   className: 'support-comparison__status--warning' },
  critical: { icon: '🔴', label: 'Crítico',  className: 'support-comparison__status--critical' },
};

export default function SupportComparison({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="support-comparison glass-card">
        <div className="support-comparison__title">⚖️ Comparación de Sostenimiento</div>
        <div className="support-comparison__empty">
          No hay datos de comparación de sostenimiento disponibles.
        </div>
      </div>
    );
  }

  return (
    <div className="support-comparison glass-card">
      <div className="support-comparison__title">
        ⚖️ Comparación de Sostenimiento: Contrato vs. Estándar
      </div>
      <div className="support-comparison__subtitle">
        Análisis por tramo — Requisitos contractuales comparados con estándares geotécnicos internacionales (Bieniawski RMR / Barton Q-System)
      </div>

      <div className="support-comparison__cards">
        {data.map((item, i) => {
          const statusCfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.warning;

          return (
            <div
              key={i}
              className={`support-comparison__card support-comparison__card--${item.status}`}
            >
              {/* Card header */}
              <div className="support-comparison__card-header">
                <div className="support-comparison__section">{item.section}</div>
                <span className={`support-comparison__status-badge ${statusCfg.className}`}>
                  {statusCfg.icon} {statusCfg.label}
                </span>
              </div>

              <div className="support-comparison__rock-class">
                🪨 {item.rock_class}
              </div>

              {/* Comparison columns */}
              <div className="support-comparison__grid">
                <div className="support-comparison__col">
                  <div className="support-comparison__col-label support-comparison__col-label--contract">
                    📄 Soporte del Contrato
                  </div>
                  <div className="support-comparison__col-value">
                    {item.contract_support}
                  </div>
                </div>

                <div className="support-comparison__col-divider">
                  <span className="support-comparison__vs">VS</span>
                </div>

                <div className="support-comparison__col">
                  <div className="support-comparison__col-label support-comparison__col-label--standard">
                    📐 Soporte Estándar
                  </div>
                  <div className="support-comparison__col-value">
                    {item.standard_support}
                  </div>
                </div>
              </div>

              {/* Recommendation */}
              <div className="support-comparison__recommendation">
                <div className="support-comparison__rec-label">💡 Recomendación del Agente</div>
                <div className="support-comparison__rec-text">{item.recommendation}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
