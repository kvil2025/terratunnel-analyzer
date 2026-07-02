import React, { useEffect, useRef } from 'react';

function getAgentTagClass(agent) {
  const name = (agent || '').toLowerCase();
  if (name.includes('geotech')) return 'agent-console__agent-tag--geotech';
  if (name.includes('contract')) return 'agent-console__agent-tag--contract';
  if (name.includes('director') || name.includes('tunnel')) return 'agent-console__agent-tag--director';
  return 'agent-console__agent-tag--orchestrator';
}

function getAgentShortName(agent) {
  const name = (agent || '').toLowerCase();
  if (name.includes('geotech')) return 'GEO';
  if (name.includes('contract')) return 'CTR';
  if (name.includes('director') || name.includes('tunnel')) return 'DIR';
  return 'ORC';
}

export default function AgentConsole({ thinkingLog, status }) {
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [thinkingLog]);

  const statusLabel =
    status === 'running' ? 'Ejecutando…' :
    status === 'done' ? 'Completado' : 'Esperando';

  return (
    <div className="agent-console glass-card">
      <div className="agent-console__header">
        <div className="agent-console__title">
          🤖 Consola de Agentes
        </div>
        <span className={`agent-console__status agent-console__status--${status}`}>
          {status === 'running' && <span className="spinner" style={{ width: 12, height: 12, borderWidth: 2, marginRight: 4, display: 'inline-block', verticalAlign: 'middle' }}></span>}
          {statusLabel}
        </span>
      </div>

      <div className="agent-console__log" ref={logRef}>
        {thinkingLog.length === 0 ? (
          <div className="agent-console__empty">
            <div className="agent-console__empty-icon">🏔️</div>
            <div>Los agentes están en espera.<br/>Carga una especificación y presiona <strong>Analizar</strong> para iniciar.</div>
          </div>
        ) : (
          thinkingLog.map((entry, i) => (
            <div className="agent-console__entry" key={i}>
              <span className={`agent-console__agent-tag ${getAgentTagClass(entry.agent)}`}>
                {getAgentShortName(entry.agent)}
              </span>
              <span className="agent-console__message">{entry.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
