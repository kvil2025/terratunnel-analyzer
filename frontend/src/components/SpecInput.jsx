import React, { useRef, useState } from 'react';

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

const ACCEPTED_TYPES = {
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/msword': '.doc',
  'text/plain': '.txt',
};

export default function SpecInput({ specText, onSpecChange, onAnalyze, onLoadSample, onFileUpload, isLoading }) {
  const charCount = specText.length;
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const MAX_FILE_SIZE_MB = isLocal ? 50 : 4;
  const [fileSizeError, setFileSizeError] = useState(null);

  const handleFile = (file) => {
    if (!file) return;
    setFileSizeError(null);

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
      alert('Formato no soportado. Use PDF, DOCX o TXT.');
      return;
    }

    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_FILE_SIZE_MB) {
      setFileSizeError(
        isLocal
          ? `El archivo (${sizeMB.toFixed(1)} MB) excede el límite de ${MAX_FILE_SIZE_MB} MB.`
          : `El archivo (${sizeMB.toFixed(1)} MB) excede el límite de Vercel (${MAX_FILE_SIZE_MB} MB). Para documentos grandes, ejecuta localmente: http://localhost:8000`
      );
      return;
    }

    setUploadedFile(file);

    // For TXT files, also show content in textarea
    if (ext === 'txt') {
      const reader = new FileReader();
      reader.onload = (e) => onSpecChange(e.target.result);
      reader.readAsText(file);
    } else {
      onSpecChange(`[Documento cargado: ${file.name} — ${(file.size / 1024).toFixed(1)} KB]\n\nEl análisis se ejecutará directamente sobre el contenido extraído del archivo.`);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleFileInput = (e) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleAnalyzeClick = () => {
    if (uploadedFile && !uploadedFile.name.endsWith('.txt')) {
      // For PDF/DOCX, use the file upload endpoint
      onFileUpload(uploadedFile);
    } else {
      // For text input or TXT files, use the text endpoint
      onAnalyze();
    }
  };

  const handleClear = () => {
    setUploadedFile(null);
    onSpecChange('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="spec-input glass-card">
      <label className="spec-input__label" htmlFor="spec-textarea">
        📄 Especificación Técnica / Contrato del Túnel
      </label>

      {/* Drop zone */}
      <div
        className={`spec-input__dropzone ${dragActive ? 'spec-input__dropzone--active' : ''} ${uploadedFile ? 'spec-input__dropzone--has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isLoading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.txt"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={isLoading}
        />
        {uploadedFile ? (
          <div className="spec-input__file-info">
            <span className="spec-input__file-icon">
              {uploadedFile.name.endsWith('.pdf') ? '📕' : uploadedFile.name.endsWith('.txt') ? '📝' : '📘'}
            </span>
            <span className="spec-input__file-name">{uploadedFile.name}</span>
            <span className="spec-input__file-size">{(uploadedFile.size / 1024).toFixed(1)} KB</span>
            <button
              className="spec-input__file-remove"
              onClick={(e) => { e.stopPropagation(); handleClear(); }}
              title="Remover archivo"
            >✕</button>
          </div>
        ) : (
          <div className="spec-input__drop-prompt">
            <span className="spec-input__drop-icon">📂</span>
            <span>Arrastra un archivo aquí o haz clic para seleccionar</span>
            <span className="spec-input__drop-formats">PDF, DOCX, TXT</span>
          </div>
        )}
      </div>

      {/* File size error */}
      {fileSizeError && (
        <div className="spec-input__size-error">
          ⚠️ {fileSizeError}
        </div>
      )}

      {/* Text area (still available for pasting) */}
      <textarea
        id="spec-textarea"
        className="spec-input__textarea"
        value={specText}
        onChange={(e) => { onSpecChange(e.target.value); setUploadedFile(null); }}
        placeholder="...o pega aquí las especificaciones técnicas, cláusulas contractuales, o extractos del GBR de tu proyecto de túnel"
        disabled={isLoading}
      />

      <div className="spec-input__actions">
        <button
          id="btn-analyze"
          className="btn btn--primary"
          onClick={handleAnalyzeClick}
          disabled={isLoading || (charCount < 20 && !uploadedFile)}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Analizando…
            </>
          ) : (
            <>🔍 Analizar {uploadedFile ? 'Documento' : 'Especificaciones'}</>
          )}
        </button>

        <button
          id="btn-load-sample"
          className="btn btn--secondary"
          onClick={() => { setUploadedFile(null); onLoadSample(SAMPLE_SPEC); }}
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
