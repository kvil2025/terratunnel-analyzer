import React from 'react';

const SAMPLE_SPEC = `PROYECTO: TÚNEL VIAL LOS ANDES — TRAMO KM 0+000 A KM 4+200
LONGITUD TOTAL: 4.200 metros
SECCIÓN: Herradura modificada, 12.5m de ancho x 9.8m de alto (área ~95 m²)
MÉTODO DE EXCAVACIÓN: Convencional — Perforación y Voladura (Drill & Blast)

=== CONDICIONES GEOLÓGICAS (Extracto del GBR) ===

Tramo 1 (Km 0+000 - Km 1+500): Granito masivo a ligeramente fracturado.
  RMR: 55-70 (Clase II-III). Q-system: 8-15.
  Sostenimiento Tipo I: Pernos puntuales de 3m, shotcrete de 50mm donde necesario.

Tramo 2 (Km 1+500 - Km 2+400): Granodiorita moderada a altamente fracturada.
  Roca de calidad regular a pobre. Q-system: Q=0.4.
  RMR: 41-60 (Clase III — roca regular).
  Sostenimiento Tipo II: Pernos sistemáticos de 3m a 2.0m de espaciamiento.

Tramo 3 (Km 2+400 - Km 3+100): Zona de falla con roca muy fracturada y arcillas.
  RMR: 30-35 (Clase IV — roca pobre).
  Presencia de arcillas montmorilloníticas en relleno de fallas.
  Cobertura: 120-180m. Nivel freático 40m sobre clave del túnel.
  Presión de agua estimada: hasta 5 bar en zona de falla (Km 2+800-2+950).
  Sostenimiento Tipo III: Pernos de anclaje puntuales sin shotcrete.

Tramo 4 (Km 3+100 - Km 4+200): Gneis de buena calidad.
  RMR: 60-75 (Clase II). Q-system: 10-25.
  Sostenimiento Tipo I.

Avance de excavación propuesto: 3-4m para todos los tramos.

=== CLÁUSULAS CONTRACTUALES (Extracto) ===

Cláusula 4.12 — Condiciones del Subsuelo:
"El Contratista acepta y asume todos los riesgos derivados de las condiciones
del subsuelo encontradas durante la excavación del túnel, incluyendo pero no
limitado a: variaciones en la clasificación de roca, presencia de agua
subterránea, zonas de falla, y cualquier otra condición geológica adversa.
El Contratista declara haber realizado su propia investigación del sitio."

Cláusula 20.1 — Notificación de Reclamos:
"Todo reclamo deberá ser notificado por escrito dentro de los 7 días
calendario siguientes a la ocurrencia del evento que da origen al reclamo.
La falta de notificación oportuna constituirá una renuncia irrevocable
al derecho de reclamo."

Sección 5.1 — Control de Aguas:
"El Contratista implementará las medidas necesarias para el control de
aguas subterráneas durante la excavación."

Sección 7.2 — Monitoreo Geotécnico:
"Se instalarán puntos de convergencia cada 25m a lo largo del túnel."

Tabla de Cantidades — Ítem 4.3 — Sostenimiento:
"Sostenimiento completo del túnel: precio global por metro lineal
de túnel excavado. Incluye todos los tipos de sostenimiento."

Cláusula 20 — Resolución de Disputas:
"Toda disputa será resuelta mediante arbitraje ad-hoc bajo las
reglas de la cámara de comercio local."`;

export default function SpecInput({ specText, onSpecChange, onAnalyze, onLoadSample, isLoading }) {
  const charCount = specText.length;

  return (
    <div className="spec-input glass-card">
      <label className="spec-input__label" htmlFor="spec-textarea">
        📄 Especificación Técnica / Contrato del Túnel
      </label>

      <textarea
        id="spec-textarea"
        className="spec-input__textarea"
        value={specText}
        onChange={(e) => onSpecChange(e.target.value)}
        placeholder="Pega aquí las especificaciones técnicas, cláusulas contractuales, o extractos del GBR de tu proyecto de túnel…"
        disabled={isLoading}
      />

      <div className="spec-input__actions">
        <button
          id="btn-analyze"
          className="btn btn--primary"
          onClick={onAnalyze}
          disabled={isLoading || charCount < 20}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Analizando…
            </>
          ) : (
            <>🔍 Analizar Especificaciones</>
          )}
        </button>

        <button
          id="btn-load-sample"
          className="btn btn--secondary"
          onClick={() => onLoadSample(SAMPLE_SPEC)}
          disabled={isLoading}
        >
          📋 Cargar Ejemplo
        </button>

        {charCount > 0 && (
          <span className="spec-input__char-count">{charCount.toLocaleString()} caracteres</span>
        )}
      </div>
    </div>
  );
}
