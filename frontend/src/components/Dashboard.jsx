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
    if (typeof f === 'string') {
      return { id: `F-${i + 1}`, severity: 'medium', title: '', description: f };
    }

    // If finding has 'type: text' with raw JSON in description, try to parse it
    if (f.type === 'text' && f.description && f.description.startsWith('{')) {
      try {
        const parsed = JSON.parse(f.description);
        const innerFindings = parsed.findings || [parsed];
        return innerFindings.map((inner, j) => normalizeFields(inner, `F-${i + 1}.${j + 1}`));
      } catch { /* fall through */ }
    }

    return normalizeFields(f, `F-${i + 1}`);
  }).flat();

  if (normalized.length === 0) return null;

  return (
    <div className="findings-section glass-card">
      <div className="findings-section__title">{icon} {title} ({normalized.length})</div>
      <div className="findings-cards">
        {normalized.map((f, i) => (
          <div key={f.id || i} className={`finding-card finding-card--${f.severity}`}>
            {/* Header: ID + Severity + Page */}
            <div className="finding-card__header">
              <span className="finding-card__id">{f.id}</span>
              <SeverityBadge severity={f.severity} />
              {f.page_number && (
                <span className="finding-card__page">📄 {f.page_number}</span>
              )}
              {f.category && (
                <span className="finding-card__category-tag">{f.category}</span>
              )}
            </div>

            {/* Title */}
            <div className="finding-card__title">{f.title}</div>

            {/* Description */}
            <div className="finding-card__description">{f.description}</div>

            {/* Quote (blockquote) */}
            {f.quote && (
              <blockquote className="finding-card__quote">
                <span className="finding-card__quote-icon">❝</span>
                {f.quote}
              </blockquote>
            )}

            {/* References + Action */}
            <div className="finding-card__footer">
              <div className="finding-card__refs">
                {f.spec_reference && (
                  <span className="finding-card__ref-tag finding-card__ref-tag--doc">
                    📎 {f.spec_reference}
                  </span>
                )}
                {f.standard_reference && (
                  <span className="finding-card__ref-tag finding-card__ref-tag--std">
                    📐 {f.standard_reference}
                  </span>
                )}
              </div>
              {f.recommended_action && (
                <div className="finding-card__action">
                  <span className="finding-card__action-label">✅ Acción:</span> {f.recommended_action}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function normalizeFields(f, fallbackId) {
  return {
    id: f.id || fallbackId,
    severity: f.severity || f.combined_severity || f.risk_level || 'medium',
    title: f.title || f.finding || f.issue || f.name || '',
    description: f.description || f.detail || f.explanation || f.analysis || '',
    category: f.category || f.type || f.area || '',
    page_number: f.page_number || f.page || f.pagina || '',
    quote: f.quote || f.cita || f.excerpt || f.text_evidence || '',
    spec_reference: f.spec_reference || f.clause_reference || f.reference || f.clause || '',
    standard_reference: f.standard_reference || f.contract_finding_id || f.norm || '',
    recommended_action: f.recommended_action || f.recommendation || f.action || f.mitigation || '',
    risk_owner: f.risk_owner || '',
  };
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
  const norm = (findings) => findings.map((f, i) => normalizeFields(f, `F-${i+1}`));
  const geotechFindings = norm(report.geotech?.findings || []);
  const contractFindings = norm(report.contract?.findings || []);
  const crossDomain = norm(report.cross_domain_findings || []);
  const supportComp = report.support_comparison || [];

  const severityColor = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' };

  const findingToCard = (f) => `
    <div style="border-left: 4px solid ${severityColor[f.severity] || '#64748b'}; background: rgba(17,24,39,0.5); border-radius: 0 12px 12px 0; padding: 1.25rem; margin-bottom: 1rem;">
      <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.5rem;">
        <span style="font-family: monospace; font-weight: 700; font-size: 0.78rem; color: #22d3ee; background: rgba(6,182,212,0.1); padding: 0.15rem 0.5rem; border-radius: 4px;">${f.id}</span>
        <span class="badge badge--${f.severity}">${f.severity.toUpperCase()}</span>
        ${f.page_number ? `<span style="font-size: 0.75rem; color: #f59e0b; background: rgba(245,158,11,0.1); padding: 0.15rem 0.5rem; border-radius: 4px;">📄 ${f.page_number}</span>` : ''}
        ${f.category ? `<span style="font-size: 0.68rem; color: #64748b; background: rgba(100,116,139,0.12); padding: 0.12rem 0.45rem; border-radius: 4px; text-transform: uppercase;">${f.category}</span>` : ''}
      </div>
      <div style="font-weight: 700; font-size: 0.95rem; color: #f1f5f9; margin-bottom: 0.4rem;">${f.title}</div>
      <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 0.5rem;">${f.description}</div>
      ${f.quote ? `<blockquote style="background: rgba(6,182,212,0.05); border-left: 3px solid #22d3ee; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.8rem; color: #94a3b8; font-style: italic; border-radius: 0 8px 8px 0;">❝ ${f.quote}</blockquote>` : ''}
      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
        ${f.spec_reference ? `<span style="font-size: 0.72rem; font-family: monospace; background: rgba(6,182,212,0.1); color: #22d3ee; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid rgba(6,182,212,0.2);">📎 ${f.spec_reference}</span>` : ''}
        ${f.standard_reference ? `<span style="font-size: 0.72rem; font-family: monospace; background: rgba(245,158,11,0.1); color: #f59e0b; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid rgba(245,158,11,0.2);">📐 ${f.standard_reference}</span>` : ''}
      </div>
      ${f.recommended_action ? `<div style="font-size: 0.8rem; color: #22c55e; background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15); border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem;">✅ <strong>Acción:</strong> ${f.recommended_action}</div>` : ''}
    </div>`;

  const supportRows = supportComp.map(s => `
    <tr class="row--${s.status}">
      <td><strong>${s.section || ''}</strong><br>${s.rock_class || ''}</td>
      <td>${s.contract_support || ''}</td>
      <td>${s.standard_support || ''}</td>
      <td>${s.recommendation || ''}</td>
    </tr>
  `).join('');

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>TerraTunnel Analyzer — Reporte</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', 'Inter', sans-serif; background: #111827; color: #e2e8f0; padding: 2rem; line-height: 1.6; max-width: 900px; margin: 0 auto; }
    h1 { color: #22d3ee; margin-bottom: 0.5rem; }
    h2 { color: #f1f5f9; border-bottom: 1px solid #374151; padding-bottom: 0.5rem; margin: 2rem 0 1rem; }
    .meta { color: #64748b; font-size: 0.85rem; margin-bottom: 2rem; }
    .risk-badge { display: inline-block; padding: 0.4rem 1.2rem; border-radius: 8px; font-weight: 700; font-size: 1.1rem; text-transform: uppercase; }
    .risk-badge--critical { background: rgba(239,68,68,0.2); color: #ef4444; }
    .risk-badge--high { background: rgba(249,115,22,0.2); color: #f97316; }
    .risk-badge--medium { background: rgba(234,179,8,0.2); color: #eab308; }
    .risk-badge--low { background: rgba(34,197,94,0.2); color: #22c55e; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    th { text-align: left; padding: 0.6rem; background: rgba(17,24,39,0.8); color: #64748b; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid #374151; }
    td { padding: 0.75rem; border-bottom: 1px solid rgba(55,65,81,0.3); font-size: 0.85rem; vertical-align: top; }
    .badge { padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
    .badge--critical { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge--high { background: rgba(249,115,22,0.15); color: #f97316; }
    .badge--medium { background: rgba(234,179,8,0.15); color: #eab308; }
    .badge--low { background: rgba(34,197,94,0.15); color: #22c55e; }
    .summary-block { background: rgba(17,24,39,0.5); border: 1px solid #374151; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; white-space: pre-wrap; }
    @media print { body { background: #fff; color: #111; max-width: 100%; } blockquote { border-left-color: #0891b2 !important; } }
  </style>
</head>
<body>
  <h1>⛏️ TerraTunnel Analyzer — Reporte de Análisis</h1>
  <div class="meta">Generado: ${new Date().toLocaleString('es-ES')} · Modelo: Gemini 2.5 Flash · Análisis: ${(report.elapsed_seconds || 0).toFixed(1)}s</div>

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
  ${geotechFindings.map(findingToCard).join('')}

  <h2>📜 Hallazgos Contractuales (${contractFindings.length})</h2>
  ${contractFindings.map(findingToCard).join('')}

  ${crossDomain.length > 0 ? `
  <h2>🔗 Conflictos Inter-disciplinarios (${crossDomain.length})</h2>
  ${crossDomain.map(findingToCard).join('')}` : ''}

  <div style="text-align: center; margin-top: 3rem; color: #64748b; font-size: 0.78rem;">
    TerraTunnel Analyzer · Multi-Agent Contract & Spec Analyzer · Powered by Gemini 2.5 Flash
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
