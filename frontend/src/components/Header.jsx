import React from 'react';

export default function Header({ mode }) {
  const isDemo = mode === 'demo';

  return (
    <header className="header">
      <div className="header__brand">
        <div className="header__icon" aria-hidden="true">⛏️</div>
        <div>
          <div className="header__title">TerraTunnel Analyzer</div>
          <div className="header__subtitle">Multi-Agent Contract & Spec Analyzer · GLM-5.2</div>
        </div>
      </div>

      <div className={`header__badge ${isDemo ? 'header__badge--demo' : 'header__badge--live'}`}>
        <span className="header__badge-dot"></span>
        {isDemo ? 'Modo Demo' : 'Modo Live — GLM-5.2'}
      </div>
    </header>
  );
}
