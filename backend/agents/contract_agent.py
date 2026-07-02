"""
TerraTunnel Analyzer — Contractual Risk Specialist Agent
=========================================================
Analyses tunnel construction contracts for risk-allocation issues,
GBR compliance, FIDIC Emerald Book alignment, and claims exposure.

Knowledge base references:
  - FIDIC Emerald Book (Conditions of Contract for Underground Works, 2019)
  - ASCE MOP 154 — Geotechnical Baseline Reports
  - ITA-AITES contractual best practices
  - Differing Site Conditions (DSC) clause standards
"""

from __future__ import annotations

from typing import Any

from .core import Agent

SYSTEM_PROMPT = """\
You are **Contract-Risk-Analyst**, a senior tunnel construction lawyer and claims \
specialist with expertise in FIDIC Emerald Book, NEC4, and international tunnel \
contract dispute resolution.

Your task is to review tunnel contract clauses, GBR (Geotechnical Baseline Report) \
provisions, and technical specifications from a **contractual risk perspective**. \
You MUST return your analysis as a JSON object with this exact schema:

```json
{
  "findings": [
    {
      "id": "CTR-001",
      "type": "risk_transfer" | "ambiguity" | "omission" | "non_compliance" | "recommendation",
      "severity": "low" | "medium" | "high" | "critical",
      "category": "risk_allocation" | "gbr_compliance" | "dsc_clause" | "payment" | "claims_notice" | "dispute_resolution" | "force_majeure" | "variation",
      "title": "Short title",
      "description": "Detailed legal/contractual explanation",
      "clause_reference": "Contract clause reference",
      "standard_reference": "FIDIC / NEC / ITA reference",
      "risk_owner": "owner" | "contractor" | "shared" | "unclear",
      "recommended_action": "What should be amended"
    }
  ],
  "risk_level": "low" | "medium" | "high" | "critical",
  "confidence": 0.0 to 1.0,
  "summary": "Executive summary of contractual risk findings"
}
```

## Key Analysis Points:
1. **Risk Allocation Fairness**: Identify clauses that shift disproportionate \
   ground risk to the contractor contrary to FIDIC Emerald Book principles.
2. **GBR Adequacy**: Evaluate whether the GBR provides clear, measurable baselines \
   for each geotechnical parameter (rock class distribution, groundwater ingress, \
   fault zone width, etc.). Flag vague or unquantified baselines.
3. **DSC Clause Completeness**: Verify that a proper Differing Site Conditions \
   clause exists and provides relief for Type I (conditions differing from GBR) \
   and Type II (unknown physical conditions).
4. **Claims Notice Periods**: Check if claims notification periods are \
   unreasonably short (< 28 days is aggressive for underground works).
5. **Payment Mechanisms**: Assess whether measurement methods and payment \
   triggers are appropriate for underground work variability.
6. **Dispute Resolution**: Verify that a Dispute Adjudication Board (DAB) or \
   similar real-time dispute mechanism exists for underground works.
7. **Variation Procedures**: Check if there are clear mechanisms for variations \
   when actual ground conditions require support class changes.
"""


class ContractAgent(Agent):
    """Contractual risk specialist agent for tunnel contracts."""

    def __init__(self) -> None:
        super().__init__(name="Contract-Risk-Analyst", system_prompt=SYSTEM_PROMPT)

    def _demo_findings(
        self, user_input: str
    ) -> tuple[list[dict[str, Any]], str, float]:
        findings = [
            {
                "id": "CTR-001",
                "type": "risk_transfer",
                "severity": "critical",
                "category": "risk_allocation",
                "title": "Transferencia total del riesgo geológico al contratista",
                "description": (
                    "La Cláusula 4.12 establece que 'el Contratista asume todos los "
                    "riesgos derivados de las condiciones del subsuelo encontradas "
                    "durante la excavación'. Esta disposición contradice directamente "
                    "el principio fundamental del FIDIC Emerald Book (Sub-Clause 4.12) "
                    "que establece un sistema de riesgo compartido basado en el GBR. "
                    "Una transferencia total del riesgo geológico genera: (1) sobrecostos "
                    "en las ofertas por contingencias excesivas, (2) incentivos perversos "
                    "para sub-diseñar el sostenimiento, y (3) alta probabilidad de "
                    "reclamaciones y disputas."
                ),
                "clause_reference": "Cláusula 4.12 — Condiciones Imprevistas del Subsuelo",
                "standard_reference": "FIDIC Emerald Book Sub-Clause 4.12; ITA-AITES Contractual Practices (2011)",
                "risk_owner": "contractor",
                "recommended_action": (
                    "Reemplazar con cláusula de riesgo compartido basada en GBR: "
                    "condiciones dentro de las líneas base → riesgo del contratista; "
                    "condiciones más adversas que la línea base → derecho a compensación "
                    "de tiempo y costo conforme Sub-Clause 4.12 del Emerald Book."
                ),
            },
            {
                "id": "CTR-002",
                "type": "ambiguity",
                "severity": "high",
                "category": "gbr_compliance",
                "title": "GBR con líneas base cualitativas, no cuantificables",
                "description": (
                    "El GBR describe las condiciones esperadas como 'roca de calidad "
                    "regular a pobre' sin especificar rangos numéricos de RMR, Q, GSI "
                    "o porcentajes de distribución por clase de roca a lo largo del "
                    "trazado. Según ASCE MOP 154, las líneas base deben ser "
                    "cuantificables y medibles para ser contractualmente ejecutables. "
                    "Un GBR vago impide determinar objetivamente si las condiciones "
                    "encontradas difieren de las previstas."
                ),
                "clause_reference": "GBR Sección 3 — Condiciones Geotécnicas de Línea Base",
                "standard_reference": "ASCE MOP 154 (2007), Sección 4.2; Essex (2007) Best Practices",
                "risk_owner": "unclear",
                "recommended_action": (
                    "Reformular el GBR con líneas base cuantificadas: (1) distribución "
                    "porcentual por clase de roca por tramo, (2) rangos RMR/Q específicos, "
                    "(3) tasas máximas de ingreso de agua en L/min por 10m de túnel, "
                    "(4) ancho máximo de zonas de falla en metros."
                ),
            },
            {
                "id": "CTR-003",
                "type": "omission",
                "severity": "high",
                "category": "dsc_clause",
                "title": "Ausencia de cláusula de Condiciones Diferentes del Sitio (DSC)",
                "description": (
                    "El contrato no contiene una cláusula explícita de Differing Site "
                    "Conditions (DSC) que defina el mecanismo de alivio cuando las "
                    "condiciones encontradas difieren materialmente del GBR. Sin esta "
                    "cláusula, el contratista no tiene un camino contractual claro para "
                    "reclamar costos adicionales por condiciones imprevistas, lo que "
                    "incrementa el riesgo de litigio."
                ),
                "clause_reference": "No encontrada — Omisión identificada",
                "standard_reference": "FIDIC Emerald Book Sub-Clause 4.12; ASCE MOP 154 Sección 5",
                "risk_owner": "contractor",
                "recommended_action": (
                    "Incorporar cláusula DSC con dos tipos de condiciones: "
                    "Tipo I (condiciones que difieren del GBR) y Tipo II (condiciones "
                    "físicas desconocidas que un contratista experimentado no habría "
                    "podido prever). Establecer procedimiento de notificación de 28 días."
                ),
            },
            {
                "id": "CTR-004",
                "type": "risk_transfer",
                "severity": "medium",
                "category": "claims_notice",
                "title": "Plazo de notificación de reclamos excesivamente corto (7 días)",
                "description": (
                    "La Cláusula 20.1 establece un plazo de notificación de reclamos "
                    "de solo 7 días calendario. En obras subterráneas, la evaluación "
                    "completa del impacto de condiciones geológicas adversas puede "
                    "requerir semanas de análisis geotécnico. El estándar FIDIC "
                    "establece 28 días, y la práctica internacional para obras "
                    "subterráneas recomienda no menos de 21 días."
                ),
                "clause_reference": "Cláusula 20.1 — Notificación de Reclamos",
                "standard_reference": "FIDIC Emerald Book Sub-Clause 20.2; ITA Best Practice (2011)",
                "risk_owner": "contractor",
                "recommended_action": (
                    "Extender el plazo de notificación a mínimo 28 días conforme "
                    "FIDIC, con provisión para notificación provisional cuando el "
                    "alcance total del impacto aún no pueda determinarse."
                ),
            },
            {
                "id": "CTR-005",
                "type": "omission",
                "severity": "medium",
                "category": "dispute_resolution",
                "title": "Sin mecanismo de resolución de disputas en tiempo real (DAB)",
                "description": (
                    "El contrato no establece un Dispute Adjudication Board (DAB) "
                    "permanente. Para obras subterráneas de larga duración, un DAB "
                    "permanente es esencial para resolver disputas sobre clasificación "
                    "de roca y medición de cantidades sin paralizar la obra."
                ),
                "clause_reference": "Cláusula 20 — Resolución de Disputas",
                "standard_reference": "FIDIC Emerald Book Clause 21; ICC DRB Rules",
                "risk_owner": "shared",
                "recommended_action": (
                    "Establecer un DAB permanente de tres miembros (un ingeniero "
                    "geotécnico, un ingeniero de túneles, y un abogado de construcción) "
                    "con visitas regulares al sitio cada 90 días."
                ),
            },
            {
                "id": "CTR-006",
                "type": "non_compliance",
                "severity": "high",
                "category": "payment",
                "title": "Medición de sostenimiento a precio global sin considerar variabilidad geológica",
                "description": (
                    "Los ítems de sostenimiento (shotcrete, pernos, cerchas) están "
                    "incluidos en un precio global por metro lineal de túnel, sin "
                    "diferenciación por clase de sostenimiento. Esto penaliza al "
                    "contratista cuando las condiciones son peores que lo previsto "
                    "y no permite una medición justa del trabajo adicional ejecutado."
                ),
                "clause_reference": "Tabla de Cantidades — Ítem 4.3 Sostenimiento",
                "standard_reference": "FIDIC Emerald Book Sub-Clause 12.1; ASCE MOP 154 — Payment Recommendations",
                "risk_owner": "contractor",
                "recommended_action": (
                    "Establecer ítems de pago separados por tipo de sostenimiento "
                    "(Tipo I a V) con cantidades estimadas basadas en la distribución "
                    "del GBR, y mecanismo de medición por metro lineal por clase "
                    "de sostenimiento efectivamente instalado."
                ),
            },
        ]

        return findings, "high", 0.91
