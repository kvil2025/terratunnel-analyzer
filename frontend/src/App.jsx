import React, { useState, useCallback, useEffect } from 'react';
import Header from './components/Header';
import SpecInput from './components/SpecInput';
import AgentConsole from './components/AgentConsole';
import Dashboard from './components/Dashboard';
import './index.css';

// In production (served by backend), use same origin. In dev, use localhost:8000.
const API_BASE = import.meta.env.VITE_API_BASE || (
  import.meta.env.DEV ? 'http://localhost:8000' : ''
);

export default function App() {
  const [specText, setSpecText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [thinkingLog, setThinkingLog] = useState([]);
  const [agentStatus, setAgentStatus] = useState('idle'); // idle | running | done
  const [mode, setMode] = useState('demo');
  const [error, setError] = useState(null);

  // Detect mode from backend on startup
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then(r => r.json())
      .then(data => { if (data.mode) setMode(data.mode); })
      .catch(() => {}); // silently fail if backend not reachable
  }, []);

  const handleLoadSample = useCallback((sample) => {
    setSpecText(sample);
    setReport(null);
    setThinkingLog([]);
    setAgentStatus('idle');
    setError(null);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!specText || specText.length < 20) return;

    setIsLoading(true);
    setReport(null);
    setError(null);
    setAgentStatus('running');
    setThinkingLog([
      { agent: 'Orchestrator', message: 'Iniciando análisis multi-agente…', timestamp: Date.now() / 1000 },
    ]);

    try {
      // Simulate agent progress messages for better UX
      const progressMessages = [
        { agent: 'Orchestrator', message: 'Delegando análisis geotécnico a GeoTech-Analyst…', delay: 300 },
        { agent: 'GeoTech-Analyst', message: 'Analizando clasificación de roca (RMR/Q-system)…', delay: 600 },
        { agent: 'GeoTech-Analyst', message: 'Evaluando sistemas de sostenimiento vs. estándares…', delay: 1000 },
        { agent: 'GeoTech-Analyst', message: 'Verificando condiciones de agua subterránea…', delay: 1400 },
        { agent: 'Orchestrator', message: 'Delegando análisis contractual a Contract-Risk-Analyst…', delay: 1800 },
        { agent: 'Contract-Risk-Analyst', message: 'Evaluando asignación de riesgos (FIDIC Emerald Book)…', delay: 2200 },
        { agent: 'Contract-Risk-Analyst', message: 'Analizando cláusulas GBR y DSC…', delay: 2600 },
        { agent: 'Contract-Risk-Analyst', message: 'Verificando mecanismos de pago y resolución de disputas…', delay: 3000 },
        { agent: 'Tunnel-Director', message: 'Sintetizando hallazgos inter-disciplinarios…', delay: 3400 },
        { agent: 'Tunnel-Director', message: 'Generando matriz de riesgos unificada…', delay: 3800 },
      ];

      // Fire progress messages with delays
      progressMessages.forEach(({ agent, message, delay }) => {
        setTimeout(() => {
          setThinkingLog(prev => [...prev, { agent, message, timestamp: Date.now() / 1000 }]);
        }, delay);
      });

      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec_text: specText }),
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Add real server thinking log entries
      if (data.thinking_log && Array.isArray(data.thinking_log)) {
        setThinkingLog(prev => [
          ...prev,
          ...data.thinking_log.map(entry => ({
            agent: entry.agent || 'System',
            message: entry.message || String(entry),
            timestamp: entry.timestamp || Date.now() / 1000,
          })),
        ]);
      }

      setThinkingLog(prev => [
        ...prev,
        { agent: 'Orchestrator', message: `✅ Análisis completado — ${(data.all_findings || []).length} hallazgos identificados`, timestamp: Date.now() / 1000 },
      ]);

      setReport(data);
      setAgentStatus('done');

    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
      setThinkingLog(prev => [
        ...prev,
        { agent: 'System', message: `❌ Error: ${err.message}`, timestamp: Date.now() / 1000 },
      ]);
      setAgentStatus('idle');
    } finally {
      setIsLoading(false);
    }
  }, [specText]);

  return (
    <>
      <Header mode={mode} />

      <main className="app-layout">
        {/* Input + Console side by side */}
        <div className="app-layout__row">
          <SpecInput
            specText={specText}
            onSpecChange={setSpecText}
            onAnalyze={handleAnalyze}
            onLoadSample={handleLoadSample}
            isLoading={isLoading}
          />
          <AgentConsole
            thinkingLog={thinkingLog}
            status={agentStatus}
          />
        </div>

        {/* Error display */}
        {error && (
          <div className="glass-card glass-card--amber" style={{
            padding: '1rem 1.5rem',
            borderColor: 'rgba(239, 68, 68, 0.4)',
            color: 'var(--severity-critical)',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}>
            ⚠️ {error}
            <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem', fontSize: '0.78rem' }}>
              — Verifica que el backend esté corriendo en {API_BASE}
            </span>
          </div>
        )}

        {/* Dashboard */}
        {report && (
          <div className="app-layout__full" style={{ animation: 'scale-in 0.5s var(--ease-spring)' }}>
            <Dashboard report={report} />
          </div>
        )}
      </main>
    </>
  );
}
