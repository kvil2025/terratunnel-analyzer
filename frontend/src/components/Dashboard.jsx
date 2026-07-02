import React, { useState, useCallback } from 'react';
import RiskGauge from './RiskGauge';
import RiskMatrix from './RiskMatrix';
import SupportComparison from './SupportComparison';

function SeverityBadge({ severity }) {
  return (
    <span className={`findings-table__severity-badge findings-table__severity-badge--${severity}`}>
      <span style={{
        width: 6, height: 6, borderRadius: '50%', display: 'inline-block',
        background: `var(--severity-${severity})`,
      }}></span>
      {severity}
    </span>
  );
}

function FindingsTable({ findings, title, icon }) {
  if (!findings || findings.length === 0) return null;

  // Normalize findings to handle various formats from Gemini
  const normalized = findings.map((f, i) => {
    // If finding is a string, wrap it
    if (typeof f === 'string') {
      return { id: `F-${i + 1}`, severity: 'medium', title: '', description: f, recommended_action: '' };
    }

    // If finding has 'type: text' with raw JSON in description, try to parse it
    if (f.type === 'text' && f.description && f.description.startsWith('{')) {
      try {
        const parsed = JSON.parse(f.description);
        const innerFindings = parsed.findings || [parsed];
        return innerFindings.map((inner, j) => ({
          id: inner.id || `F-${i + 1}.${j + 1}`,
          severity: inner.severity || inner.combined_severity || inner.risk_level || 'medium',
          title: inner.title || inner.finding || inner.issue || '',
          description: inner.description || inner.detail || inner.explanation || '',
          category: inner.category || inner.type || '',
          recommended_action: inner.recommended_action || inner.recommendation || inner.action || inner.mitigation || '',
          spec_reference: inner.spec_reference || inner.reference || inner.clause || '',
          standard_reference: inner.standard_reference || '',
        }));
      } catch { /* fall through */ }
    }

    // Standard normalization — handle various field names Gemini might use
    return {
      id: f.id || `F-${i + 1}`,
      severity: f.severity || f.combined_severity || f.risk_level || 'medium',
      title: f.title || f.finding || f.issue || f.name || '',
      description: f.description || f.detail || f.explanation || f.analysis || '',
      category: f.category || f.type || f.area || '',
      recommended_action: f.recommended_action || f.recommendation || f.action || f.mitigation || f.suggested_action || '',
      spec_reference: f.spec_reference || f.clause_reference || f.reference || f.clause || f.geotech_finding_id || '',
      standard_reference: f.standard_reference || f.contract_finding_id || f.norm || '',
    };
  }).flat(); // flat() handles the case where a single finding expands into multiple

  if (normalized.length === 0) return null;

  return (
    <div className="findings-section glass-card">
      <div className="findings-section__title">{icon} {title}</div>
      <div style={{ overflowX: 'auto' }}>
        <table className="findings-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Severidad</th>
              <th>Hallazgo</th>
              <th>Referencia</th>
              <th>Acción Recomendada</th>
            </tr>
          </thead>
          <tbody>
            {normalized.map((f, i) => (
              <tr key={f.id || i}>
                <td>
                  <div className="findings-table__id">{f.id}</div>
                  <div className="findings-table__category">{f.category}</div>
                </td>
                <td><SeverityBadge severity={f.severity} /></td>
                <td>
                  <div className="findings-table__title-text">{f.title}</div>
                  <div className="findings-table__description">{f.description}</div>
                </td>
                <td style={{ fontSize: '0.75rem', minWidth: 140 }}>
                  <div style={{ color: 'var(--cyan-400)', marginBottom: '0.25rem' }}>
                    {f.spec_reference || '—'}
                  </div>
                  <div style={{ color: 'var(--text-muted)' }}>
                    {f.standard_reference}
                  </div>
                </td>
                <td>
                  <div className="findings-table__action">
                    {f.recommended_action || '—'}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ExecutiveSummary({ summary }) {
  if (!summary) return null;

  // Simple markdown-like rendering for ## headers and \n
  const lines = summary.split('\n');
  const rendered = lines.map((line, i) => {
    if (line.startsWith('### ')) {
      return <h3 key={i} style={{ marginTop: '1rem', marginBottom: '0.4rem' }}>{line.replace('### ', '')}</h3>;
    }
    if (line.startsWith('## ')) {
      return <h2 key={i} style={{ marginTop: '1.2rem', marginBottom: '0.5rem', fontSize: '1.05rem' }}>{line.replace('## ', '')}</h2>;
    }
    if (line.match(/^\d+\.\s\*\*/)) {
      const text = line.replace(/\*\*/g, '');
      return <div key={i} style={{ paddingLeft: '1rem', marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>{text}</div>;
    }
    if (line.trim() === '') return <br key={i} />;
    return <p key={i} style={{ marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>{line}</p>;
  });

  return (
    <div className="executive-summary glass-card">
      <div className="executive-summary__title">📋 Resumen Ejecutivo</div>
      <div className="executive-summary__content">{rendered}</div>
    </div>
  );
}

/* ── Download Helpers ─────────────────────────────────────────── */

function downloadJSON(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `terratunnel-report-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadHTML(report) {
  const geotechFindings = report.geotech?.findings || [];
  const contractFindings = report.contract?.findings || [];
  const crossDomain = report.cross_domain_findings || [];
  const supportComp = report.support_comparison || [];

  const findingsToRows = (findings) => findings.map(f => `
    <tr>
      <td><strong>${f.id || '—'}</strong><br><small>${f.category || f.type || ''}</small></td>
      <td><span class="badge badge--${f.severity || f.combined_severity || 'medium'}">${(f.severity || f.combined_severity || 'medium').toUpperCase()}</span></td>
      <td><strong>${f.title || ''}</strong><br>${f.description || ''}</td>
      <td>${f.recommended_action || '—'}</td>
    </tr>
  `).join('');

  const supportRows = supportComp.map(s => `
    <tr class="row--${s.status}">
      <td><strong>${s.section}</strong><br>${s.rock_class}</td>
      <td>${s.contract_support}</td>
      <td>${s.standard_support}</td>
      <td>${s.recommendation}</td>
    </tr>
  `).join('');

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>TerraTunnel Analyzer — Reporte</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', 'Inter', sans-serif; background: #111827; color: #e2e8f0; padding: 2rem; line-height: 1.6; }
    h1 { color: #22d3ee; margin-bottom: 0.5rem; }
    h2 { color: #f1f5f9; border-bottom: 1px solid #374151; padding-bottom: 0.5rem; margin: 2rem 0 1rem; }
    h3 { color: #94a3b8; margin: 1.5rem 0 0.5rem; }
    .meta { color: #64748b; font-size: 0.85rem; margin-bottom: 2rem; }
    .risk-badge { display: inline-block; padding: 0.4rem 1.2rem; border-radius: 8px; font-weight: 700; font-size: 1.1rem; text-transform: uppercase; }
    .risk-badge--critical { background: rgba(239,68,68,0.2); color: #ef4444; }
    .risk-badge--high { background: rgba(249,115,22,0.2); color: #f97316; }
    .risk-badge--medium { background: rgba(234,179,8,0.2); color: #eab308; }
    .risk-badge--low { background: rgba(34,197,94,0.2); color: #22c55e; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    th { text-align: left; padding: 0.6rem 0.75rem; background: rgba(17,24,39,0.8); color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #374151; }
    td { padding: 0.75rem; border-bottom: 1px solid rgba(55,65,81,0.3); font-size: 0.85rem; vertical-align: top; }
    .badge { padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
    .badge--critical { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge--high { background: rgba(249,115,22,0.15); color: #f97316; }
    .badge--medium { background: rgba(234,179,8,0.15); color: #eab308; }
    .badge--low { background: rgba(34,197,94,0.15); color: #22c55e; }
    .row--critical td { border-left: 3px solid #ef4444; }
    .row--warning td { border-left: 3px solid #eab308; }
    .row--ok td { border-left: 3px solid #22c55e; }
    .summary-block { background: rgba(17,24,39,0.5); border: 1px solid #374151; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; white-space: pre-wrap; }
    @media print { body { background: #fff; color: #111; } th { background: #f3f4f6; color: #374151; } .risk-badge--critical, .badge--critical { color: #dc2626; } .risk-badge--high, .badge--high { color: #ea580c; } }
  </style>
</head>
<body>
  <h1>⛏️ TerraTunnel Analyzer — Reporte de Análisis</h1>
  <div class="meta">Generado: ${new Date().toLocaleString('es-ES')} · Modelo: GLM-5.2 · Análisis: ${(report.elapsed_seconds || 0).toFixed(1)}s</div>

  <p>Nivel de riesgo global: <span class="risk-badge risk-badge--${report.overall_risk_level || 'medium'}">${(report.overall_risk_level || 'medio').toUpperCase()}</span></p>
  <p style="margin-top: 0.5rem; color: #94a3b8;">Confianza: ${Math.round((report.overall_confidence || 0) * 100)}%</p>

  ${report.executive_summary ? `<h2>📋 Resumen Ejecutivo</h2><div class="summary-block">${report.executive_summary}</div>` : ''}

  ${supportComp.length > 0 ? `
  <h2>⚖️ Comparación de Sostenimiento</h2>
  <table>
    <thead><tr><th>Tramo / Clase de Roca</th><th>Soporte del Contrato</th><th>Soporte Estándar</th><th>Recomendación</th></tr></thead>
    <tbody>${supportRows}</tbody>
  </table>` : ''}

  <h2>⛏️ Hallazgos Geotécnicos (${geotechFindings.length})</h2>
  <table><thead><tr><th>ID</th><th>Severidad</th><th>Hallazgo</th><th>Acción</th></tr></thead><tbody>${findingsToRows(geotechFindings)}</tbody></table>

  <h2>📜 Hallazgos Contractuales (${contractFindings.length})</h2>
  <table><thead><tr><th>ID</th><th>Severidad</th><th>Hallazgo</th><th>Acción</th></tr></thead><tbody>${findingsToRows(contractFindings)}</tbody></table>

  ${crossDomain.length > 0 ? `
  <h2>🔗 Conflictos Inter-disciplinarios (${crossDomain.length})</h2>
  <table><thead><tr><th>ID</th><th>Severidad</th><th>Hallazgo</th><th>Acción</th></tr></thead><tbody>${findingsToRows(crossDomain)}</tbody></table>` : ''}

  <div style="text-align: center; margin-top: 3rem; color: #64748b; font-size: 0.78rem;">
    TerraTunnel Analyzer · Multi-Agent Contract & Spec Analyzer · Powered by GLM-5.2
  </div>
</body>
</html>`;

  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `terratunnel-report-${new Date().toISOString().slice(0, 10)}.html`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Dashboard Component ─────────────────────────────────────── */

export default function Dashboard({ report }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!report) return null;

  const geotechFindings = report.geotech?.findings || [];
  const contractFindings = report.contract?.findings || [];
  const crossDomain = report.cross_domain_findings || [];
  const supportComp = report.support_comparison || [];
  const totalFindings = geotechFindings.length + contractFindings.length + crossDomain.length;

  const criticalCount = [...geotechFindings, ...contractFindings, ...crossDomain]
    .filter(f => (f.severity || f.combined_severity) === 'critical').length;
  const highCount = [...geotechFindings, ...contractFindings, ...crossDomain]
    .filter(f => (f.severity || f.combined_severity) === 'high').length;

  const tabs = [
    { id: 'overview', label: 'Vista General', icon: '📊' },
    { id: 'comparison', label: 'Sostenimiento', icon: '⚖️', count: supportComp.length },
    { id: 'geotech', label: 'Geotécnico', icon: '⛏️', count: geotechFindings.length },
    { id: 'contract', label: 'Contractual', icon: '📜', count: contractFindings.length },
    { id: 'crossdomain', label: 'Inter-disciplinario', icon: '🔗', count: crossDomain.length },
    { id: 'summary', label: 'Resumen', icon: '📋' },
  ];

  return (
    <div className="dashboard">
      {/* Metrics row */}
      <div className="dashboard__metrics">
        <div className="metric-card glass-card">
          <div className={`metric-card__value metric-card__value--${report.overall_risk_level || 'medium'}`}>
            {(report.overall_risk_level || 'MEDIO').toUpperCase()}
          </div>
          <div className="metric-card__label">Nivel de Riesgo</div>
        </div>
        <div className="metric-card glass-card">
          <div className="metric-card__value metric-card__value--cyan">{totalFindings}</div>
          <div className="metric-card__label">Hallazgos Totales</div>
        </div>
        <div className="metric-card glass-card">
          <div className="metric-card__value metric-card__value--critical">{criticalCount}</div>
          <div className="metric-card__label">Críticos</div>
        </div>
        <div className="metric-card glass-card">
          <div className="metric-card__value metric-card__value--high">{highCount}</div>
          <div className="metric-card__label">Altos</div>
        </div>
      </div>

      {/* Tab navigation + download buttons */}
      <div className="dashboard__toolbar">
        <div className="section-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`section-tab ${activeTab === tab.id ? 'section-tab--active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon} {tab.label}
              {tab.count !== undefined && (
                <span className="section-tab__count">{tab.count}</span>
              )}
            </button>
          ))}
        </div>

        <div className="dashboard__downloads">
          <button
            className="btn btn--secondary btn--sm"
            onClick={() => downloadJSON(report)}
            title="Descargar reporte completo en formato JSON"
          >
            📥 JSON
          </button>
          <button
            className="btn btn--secondary btn--sm"
            onClick={() => downloadHTML(report)}
            title="Descargar reporte imprimible en HTML"
          >
            🖨️ Reporte HTML
          </button>
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <RiskGauge
            riskLevel={report.overall_risk_level || 'medium'}
            confidence={report.overall_confidence || 0.5}
          />
          <RiskMatrix riskMatrix={report.risk_matrix || []} />
        </div>
      )}

      {activeTab === 'comparison' && (
        <SupportComparison data={supportComp} />
      )}

      {activeTab === 'geotech' && (
        <FindingsTable
          findings={geotechFindings}
          title="Hallazgos Geotécnicos"
          icon="⛏️"
        />
      )}

      {activeTab === 'contract' && (
        <FindingsTable
          findings={contractFindings}
          title="Hallazgos Contractuales"
          icon="📜"
        />
      )}

      {activeTab === 'crossdomain' && (
        <FindingsTable
          findings={crossDomain}
          title="Conflictos Inter-disciplinarios"
          icon="🔗"
        />
      )}

      {activeTab === 'summary' && (
        <ExecutiveSummary summary={report.executive_summary} />
      )}

      {/* Elapsed time */}
      {report.elapsed_seconds && (
        <div style={{
          textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)', marginTop: '0.5rem',
        }}>
          Análisis completado en {report.elapsed_seconds.toFixed(1)}s · 3 agentes · GLM-5.2
        </div>
      )}
    </div>
  );
}
