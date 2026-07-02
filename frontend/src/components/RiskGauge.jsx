import React, { useEffect, useState } from 'react';

const RISK_CONFIG = {
  critical: { color: '#ef4444', label: 'CRÍTICO', angle: 162 },
  high:     { color: '#f97316', label: 'ALTO',    angle: 126 },
  medium:   { color: '#eab308', label: 'MEDIO',   angle: 90  },
  low:      { color: '#22c55e', label: 'BAJO',    angle: 36  },
};

export default function RiskGauge({ riskLevel, confidence }) {
  const [animated, setAnimated] = useState(false);
  const config = RISK_CONFIG[riskLevel] || RISK_CONFIG.medium;

  // Arc geometry: semicircle from left to right
  const cx = 100, cy = 100, r = 80;
  const totalArc = Math.PI; // 180 degrees
  const circumference = totalArc * r; // ~251.3

  const targetOffset = circumference - (config.angle / 180) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, [riskLevel]);

  // Arc path: semicircle from left (180°) to right (0°)
  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;

  return (
    <div className="risk-gauge glass-card">
      <svg className="risk-gauge__svg" viewBox="0 0 200 120">
        {/* Background arc */}
        <path d={arcPath} className="risk-gauge__bg" />

        {/* Filled arc */}
        <path
          d={arcPath}
          className="risk-gauge__fill"
          stroke={config.color}
          strokeDasharray={circumference}
          strokeDashoffset={animated ? targetOffset : circumference}
        />

        {/* Center percentage text */}
        <text
          x={cx}
          y={cy - 10}
          textAnchor="middle"
          fill={config.color}
          fontSize="28"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          {Math.round(confidence * 100)}%
        </text>
        <text
          x={cx}
          y={cy + 10}
          textAnchor="middle"
          fill="#94a3b8"
          fontSize="10"
          fontFamily="Inter, sans-serif"
        >
          confianza
        </text>
      </svg>

      <div className={`risk-gauge__label risk-gauge__label--${riskLevel}`}>
        Riesgo: {config.label}
      </div>
      <div className="risk-gauge__confidence">
        Evaluación combinada de 3 agentes especializados
      </div>
    </div>
  );
}
