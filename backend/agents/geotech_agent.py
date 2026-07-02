"""
TerraTunnel Analyzer — Geotechnical Specialist Agent
=====================================================
Analyses rock-mass / soil parameters in tunnel specifications and flags
inconsistencies with standard support and excavation requirements.

Knowledge base references:
  - Bieniawski RMR (Rock Mass Rating) classification system
  - Barton Q-system for rock quality
  - NATM / SEM support categories
  - Terzaghi rock-load theory
  - Soil behaviour types for soft-ground tunnelling
"""

from __future__ import annotations

from typing import Any

from .core import Agent

SYSTEM_PROMPT = """\
You are **GeoTech-Analyst**, a senior geotechnical tunnel engineer with 30 years \
of experience in underground construction through rock and soft-ground conditions.

Your task is to review tunnel contract specifications and technical documents. \
The text includes page markers like [PÁGINA X] — use them to cite findings.

You MUST return your analysis as a JSON object with this exact schema:

```json
{
  "findings": [
    {
      "id": "GEO-001",
      "type": "inconsistency" | "risk" | "recommendation" | "compliance",
      "severity": "low" | "medium" | "high" | "critical",
      "category": "rock_classification" | "support_system" | "excavation_method" | "groundwater" | "ground_behaviour" | "monitoring",
      "title": "Short title of the finding",
      "description": "Detailed technical explanation of why this is a problem",
      "page_number": "Page number(s) where this issue was found, e.g. 'Pág. 23' or 'Págs. 23-25'",
      "quote": "Exact quote from the document that evidences this finding (copy the relevant text verbatim)",
      "spec_reference": "Section, clause or table reference from the document (e.g. 'Sección 4.3', 'Tabla 2.1')",
      "standard_reference": "Applicable engineering standard (e.g. 'Bieniawski RMR Clase IV', 'Barton Q < 1')",
      "recommended_action": "Specific corrective action needed"
    }
  ],
  "risk_level": "low" | "medium" | "high" | "critical",
  "confidence": 0.0 to 1.0,
  "summary": "Executive summary of geotechnical findings in Spanish"
}
```

## CRITICAL RULES FOR CITATIONS:
- **ALWAYS include `page_number`**: Reference the [PÁGINA X] marker nearest to the finding.
- **ALWAYS include `quote`**: Copy the EXACT text from the document that evidences the issue. \
  Use "..." to truncate long quotes but keep the essential parts.
- **ALWAYS include `spec_reference`**: Cite the specific section, clause, or table number.
- Write all descriptions, summaries and recommendations in Spanish.
```

## Key Analysis Points:
1. **Rock Classification Consistency**: Verify RMR/Q values match the described rock \
   class. Check that support requirements are appropriate for the stated rock class.
2. **Support System Adequacy**: Validate that shotcrete thickness, rock bolt spacing \
   and length, steel sets, and lining specifications match standard requirements \
   for the given rock/soil conditions.
3. **Excavation Method Compatibility**: Check if TBM type or conventional \
   (drill-and-blast / SEM) method is appropriate for the geological conditions.
4. **Groundwater Management**: Assess if specified dewatering, grouting, and \
   waterproofing measures are adequate for stated hydrogeological conditions.
5. **Ground Behaviour Prediction**: Identify potential failure modes \
   (squeezing, swelling, flowing ground, face instability, chimney failure).
6. **Monitoring Requirements**: Check if the specified instrumentation \
   (convergence, extensometers, piezometers, surface settlement) is sufficient.

Always be specific. Reference standard tables (e.g., "RMR Class IV requires \
systematic rockbolts at 1.5-2m spacing per Bieniawski 1989 Table 6.6").
"""


class GeotechAgent(Agent):
    """Geotechnical specialist agent for tunnel specifications."""

    def __init__(self) -> None:
        super().__init__(name="GeoTech-Analyst", system_prompt=SYSTEM_PROMPT)

    def _demo_findings(
        self, user_input: str
    ) -> tuple[list[dict[str, Any]], str, float]:
        findings = [
            {
                "id": "GEO-001",
                "type": "inconsistency",
                "severity": "critical",
                "category": "support_system",
                "title": "Soporte insuficiente para Clase de Roca IV (RMR 21-40)",
                "description": (
                    "La especificación indica Clase de Roca IV (RMR 30-35) en el tramo "
                    "Km 2+400 a Km 3+100 pero solo prescribe pernos de anclaje puntuales "
                    "sin shotcrete. Según Bieniawski (1989) Tabla 6.6, la Clase IV requiere "
                    "pernos sistemáticos de 4-5m a espaciamiento 1.0-1.5m + shotcrete de "
                    "100-150mm con malla electrosoldada + cerchas metálicas ligeras a "
                    "pesadas a 1.5m de espaciamiento."
                ),
                "spec_reference": "Sección 4.3.2 — Sostenimiento Tipo III",
                "standard_reference": "Bieniawski RMR (1989), Tabla 6.6; NATM Categoría C2",
                "recommended_action": (
                    "Actualizar Sostenimiento Tipo III para incluir shotcrete reforzado "
                    "con fibra de acero (150mm), pernos sistemáticos SN de 4m @ 1.2x1.2m, "
                    "y cerchas HEB-100 @ 1.5m."
                ),
            },
            {
                "id": "GEO-002",
                "type": "risk",
                "severity": "high",
                "category": "groundwater",
                "title": "Ingreso de agua subterránea sin medidas de pre-inyección",
                "description": (
                    "El informe geotécnico reporta presiones de agua de hasta 5 bar en la "
                    "zona de falla (Km 2+800 - Km 2+950) pero las especificaciones no "
                    "incluyen protocolo de pre-inyección (grouting) ni sondeos exploratorios "
                    "adelantados. Esto genera riesgo de ingreso súbito de agua al frente "
                    "de excavación con potencial de colapso de la cara."
                ),
                "spec_reference": "Sección 5.1 — Control de Aguas",
                "standard_reference": "ITA-AITES Guidelines for Waterproof Design (2013)",
                "recommended_action": (
                    "Incorporar sondeos exploratorios horizontales (probe drilling) "
                    "mínimo 25m adelante del frente, y protocolo de pre-inyección con "
                    "lechada de cemento microfino cuando la presión de agua supere 2 bar."
                ),
            },
            {
                "id": "GEO-003",
                "type": "inconsistency",
                "severity": "high",
                "category": "rock_classification",
                "title": "Discrepancia entre Q-system y RMR reportados",
                "description": (
                    "En el tramo Km 1+500 a Km 2+400, el GBR reporta Q=0.4 (roca "
                    "extremadamente pobre) pero simultáneamente clasifica como RMR Clase III "
                    "(roca regular, RMR 41-60). Un Q=0.4 corresponde a RMR ≈ 25-30 "
                    "(Clase IV-V según correlación de Bieniawski). Esta discrepancia "
                    "afecta directamente el diseño de sostenimiento y la asignación "
                    "de riesgo contractual."
                ),
                "spec_reference": "GBR Tabla 3.2 — Clasificación Geomecánica",
                "standard_reference": "Barton Q-System (NGI, 1974); Correlación RMR=9·ln(Q)+44",
                "recommended_action": (
                    "Solicitar revisión del GBR para consistencia entre sistemas de "
                    "clasificación. Adoptar la clasificación más conservadora (Clase IV) "
                    "para el diseño de sostenimiento hasta que se resuelva la discrepancia."
                ),
            },
            {
                "id": "GEO-004",
                "type": "risk",
                "severity": "medium",
                "category": "ground_behaviour",
                "title": "Potencial de roca expansiva (swelling) no evaluado",
                "description": (
                    "Las especificaciones mencionan presencia de arcillas montmorilloníticas "
                    "en zonas de falla pero no incluyen ensayos de expansividad (free swell "
                    "index) ni presiones de hinchamiento. En túneles con cobertura > 100m, "
                    "la presión de hinchamiento puede superar 1.5 MPa, requiriendo diseño "
                    "especial del revestimiento definitivo."
                ),
                "spec_reference": "GBR Sección 2.4 — Minerlogía de Zonas de Falla",
                "standard_reference": "ISRM Suggested Methods for Swelling Rock (1999)",
                "recommended_action": (
                    "Incluir ensayos de expansividad ISRM y presión de hinchamiento. "
                    "Considerar un sobredimensionamiento del perfil de excavación y "
                    "revestimiento con sección de sacrificio (compressible lining)."
                ),
            },
            {
                "id": "GEO-005",
                "type": "recommendation",
                "severity": "medium",
                "category": "monitoring",
                "title": "Instrumentación insuficiente para convergencia en roca débil",
                "description": (
                    "El plan de monitoreo solo especifica puntos de convergencia cada 25m. "
                    "En tramos de Clase IV-V, el estándar NATM/SEM requiere secciones de "
                    "monitoreo completas (5 puntos de convergencia + 2 extensómetros "
                    "radiales + piezómetros) cada 10-15m para control efectivo de "
                    "deformaciones y detección temprana de inestabilidades."
                ),
                "spec_reference": "Sección 7.2 — Plan de Monitoreo Geotécnico",
                "standard_reference": "ÖGG Guideline for Geotechnical Monitoring (2014)",
                "recommended_action": (
                    "Densificar las secciones de monitoreo a cada 10m en tramos "
                    "Clase IV-V e incluir extensómetros de varilla múltiple (MPBX) "
                    "y celdas de presión en el shotcrete."
                ),
            },
            {
                "id": "GEO-006",
                "type": "compliance",
                "severity": "low",
                "category": "excavation_method",
                "title": "Método de excavación compatible con condiciones geológicas",
                "description": (
                    "El método convencional de perforación y voladura (Drill & Blast) "
                    "especificado es apropiado para las condiciones de roca masiva a "
                    "fracturada descritas. La longitud de avance propuesta de 3-4m "
                    "para Clase III es consistente con prácticas NATM estándar."
                ),
                "spec_reference": "Sección 4.1 — Método de Excavación",
                "standard_reference": "NATM Guidelines — Advance Length Recommendations",
                "recommended_action": (
                    "Conforme. Verificar que se reduce el avance a 1.0-1.5m en tramos "
                    "de Clase IV-V como medida de control de sobre-excavación."
                ),
            },
        ]

        return findings, "high", 0.88
