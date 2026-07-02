"""
TerraTunnel Analyzer — Multi-Agent Orchestrator
=================================================
Coordinates the Geotechnical and Contractual agents, resolves cross-domain
conflicts, and produces a unified risk report.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from .core import Agent, AgentResult, is_demo_mode
from .geotech_agent import GeotechAgent
from .contract_agent import ContractAgent

ORCHESTRATOR_PROMPT = """\
You are **Tunnel-Director**, the chief orchestrator of a multi-agent analysis \
system for tunnel construction contracts. You coordinate two specialist agents:

1. **GeoTech-Analyst**: Provides geotechnical findings (rock classification, \
   support adequacy, groundwater, monitoring).
2. **Contract-Risk-Analyst**: Provides contractual risk findings (risk allocation, \
   GBR compliance, DSC clauses, payment mechanisms).

Your job is to:
1. Identify **cross-domain conflicts** — places where geotechnical risks and \
   contractual provisions are misaligned (e.g., high face-instability risk but \
   the contract shifts all face-stability risk to the contractor).
2. Produce a **unified risk assessment** combining both analyses.
3. Prioritize the findings by overall project impact.

Return your analysis as JSON with this schema:

```json
{
  "cross_domain_findings": [
    {
      "id": "XD-001",
      "title": "Short title of cross-domain issue",
      "geotech_finding_id": "GEO-XXX",
      "contract_finding_id": "CTR-XXX",
      "description": "How these findings interact and create amplified risk",
      "combined_severity": "critical" | "high" | "medium" | "low",
      "recommended_action": "Integrated recommendation"
    }
  ],
  "overall_risk_level": "low" | "medium" | "high" | "critical",
  "overall_confidence": 0.0 to 1.0,
  "executive_summary": "Multi-paragraph executive summary in Spanish",
  "risk_matrix": [
    {
      "risk_id": "ID",
      "description": "Risk description",
      "likelihood": 1 to 5,
      "consequence": 1 to 5,
      "category": "geotechnical" | "contractual" | "cross-domain"
    }
  ]
}
```
"""


@dataclass
class AnalysisReport:
    """Complete multi-agent analysis report."""
    geotech_result: AgentResult
    contract_result: AgentResult
    orchestrator_result: AgentResult
    cross_domain_findings: list[dict[str, Any]] = field(default_factory=list)
    risk_matrix: list[dict[str, Any]] = field(default_factory=list)
    support_comparison: list[dict[str, Any]] = field(default_factory=list)
    overall_risk_level: str = "medium"
    overall_confidence: float = 0.0
    executive_summary: str = ""
    all_findings: list[dict[str, Any]] = field(default_factory=list)
    thinking_log: list[dict[str, Any]] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "geotech": self.geotech_result.to_dict(),
            "contract": self.contract_result.to_dict(),
            "orchestrator": self.orchestrator_result.to_dict(),
            "cross_domain_findings": self.cross_domain_findings,
            "risk_matrix": self.risk_matrix,
            "support_comparison": self.support_comparison,
            "overall_risk_level": self.overall_risk_level,
            "overall_confidence": self.overall_confidence,
            "executive_summary": self.executive_summary,
            "all_findings": self.all_findings,
            "thinking_log": self.thinking_log,
            "elapsed_seconds": self.elapsed_seconds,
        }


class Orchestrator:
    """Coordinates the multi-agent analysis pipeline."""

    def __init__(self) -> None:
        self.geotech_agent = GeotechAgent()
        self.contract_agent = ContractAgent()
        self.director = Agent(name="Tunnel-Director", system_prompt=ORCHESTRATOR_PROMPT)
        self.thinking_log: list[dict[str, Any]] = []

    def _log(self, agent: str, message: str) -> None:
        entry = {
            "agent": agent,
            "message": message,
            "timestamp": time.time(),
        }
        self.thinking_log.append(entry)

    def analyze(self, spec_text: str) -> AnalysisReport:
        """Run the full multi-agent analysis pipeline."""
        start = time.time()

        # ── Pre-validation: check document relevance ──────────────
        if not is_demo_mode():
            rejection = self._validate_document(spec_text)
            if rejection:
                rejection.elapsed_seconds = time.time() - start
                return rejection

        # ── Step 1: Geotechnical analysis ────────────────────────────
        self._log("Orchestrator", "Delegating geotechnical analysis to GeoTech-Analyst …")
        geotech_result = self.geotech_agent.run(
            f"Analiza las siguientes especificaciones técnicas de túnel y "
            f"proporciona tus hallazgos geotécnicos:\n\n{spec_text}"
        )
        self._log(
            "GeoTech-Analyst",
            f"Completado: {len(geotech_result.findings)} hallazgos, "
            f"nivel de riesgo: {geotech_result.risk_level}",
        )
        for entry in geotech_result.thinking_log:
            self._log("GeoTech-Analyst", entry)

        # ── Step 2: Contractual analysis ─────────────────────────────
        self._log("Orchestrator", "Delegating contractual risk analysis to Contract-Risk-Analyst …")
        contract_result = self.contract_agent.run(
            f"Analiza las siguientes cláusulas contractuales y especificaciones "
            f"de un proyecto de túnel. Identifica riesgos contractuales:\n\n{spec_text}"
        )
        self._log(
            "Contract-Risk-Analyst",
            f"Completado: {len(contract_result.findings)} hallazgos, "
            f"nivel de riesgo: {contract_result.risk_level}",
        )
        for entry in contract_result.thinking_log:
            self._log("Contract-Risk-Analyst", entry)

        # ── Step 3: Cross-domain synthesis ───────────────────────────
        self._log("Orchestrator", "Synthesizing cross-domain analysis with Tunnel-Director …")
        synthesis_input = (
            f"## Hallazgos Geotécnicos\n{json.dumps(geotech_result.findings, ensure_ascii=False, indent=2)}\n\n"
            f"## Hallazgos Contractuales\n{json.dumps(contract_result.findings, ensure_ascii=False, indent=2)}\n\n"
            f"Identifica conflictos entre hallazgos geotécnicos y contractuales, "
            f"genera la matriz de riesgos unificada, y proporciona el resumen ejecutivo."
        )

        if is_demo_mode():
            orchestrator_result = self._demo_synthesis(geotech_result, contract_result)
        else:
            orchestrator_result = self.director.run(synthesis_input)

        for entry in orchestrator_result.thinking_log:
            self._log("Tunnel-Director", entry)

        # ── Build report ─────────────────────────────────────────────
        cross_domain = []
        risk_matrix = []
        support_comparison = []
        executive_summary = ""
        overall_risk = "high"
        overall_confidence = 0.85

        try:
            orch_data = json.loads(orchestrator_result.raw_response)
            cross_domain = orch_data.get("cross_domain_findings", [])
            risk_matrix = orch_data.get("risk_matrix", [])
            support_comparison = orch_data.get("support_comparison", [])
            executive_summary = orch_data.get("executive_summary", "")
            overall_risk = orch_data.get("overall_risk_level", "high")
            overall_confidence = orch_data.get("overall_confidence", 0.85)
        except (json.JSONDecodeError, AttributeError):
            pass

        all_findings = (
            geotech_result.findings
            + contract_result.findings
            + cross_domain
        )

        elapsed = time.time() - start
        self._log("Orchestrator", f"Analysis complete in {elapsed:.1f}s — {len(all_findings)} total findings")

        return AnalysisReport(
            geotech_result=geotech_result,
            contract_result=contract_result,
            orchestrator_result=orchestrator_result,
            cross_domain_findings=cross_domain,
            risk_matrix=risk_matrix,
            support_comparison=support_comparison,
            overall_risk_level=overall_risk,
            overall_confidence=overall_confidence,
            executive_summary=executive_summary,
            all_findings=all_findings,
            thinking_log=self.thinking_log,
            elapsed_seconds=elapsed,
        )

    # ------------------------------------------------------------------
    # Document relevance validation
    # ------------------------------------------------------------------

    def _validate_document(self, spec_text: str) -> AnalysisReport | None:
        """Quick check if document is related to tunnel/underground construction.
        Returns a rejection AnalysisReport if not relevant, or None if valid.
        """
        from .core import _get_client, _model_id

        self._log("Orchestrator", "Validating document relevance …")

        # Use first 1000 chars for a fast check
        preview = spec_text[:1000]

        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=_model_id(),
                messages=[
                    {"role": "system", "content": (
                        "You are a document classifier. Determine if the following document "
                        "is related to ANY of these topics: tunnel construction, underground "
                        "excavation, geotechnical engineering, rock mechanics, TBM, drill & blast, "
                        "tunnel support systems, underground infrastructure contracts, "
                        "civil engineering specifications, or construction contracts. "
                        "Respond ONLY with valid JSON: "
                        '{\"relevant\": true/false, \"document_type\": \"brief description\", '
                        '\"reason\": \"why it is or is not relevant\"}'
                    )},
                    {"role": "user", "content": preview},
                ],
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            if result.get("relevant", True):
                doc_type = result.get("document_type", "tunnel document")
                self._log("Orchestrator", f"Document validated: {doc_type}")
                return None  # Document is valid, proceed with analysis

            # Document is NOT relevant — return rejection report
            doc_type = result.get("document_type", "documento no relacionado")
            reason = result.get("reason", "")
            self._log("Orchestrator", f"Document rejected: {doc_type} — {reason}")

            empty_result = AgentResult(
                agent_name="Orchestrator",
                raw_response=content,
                findings=[],
                risk_level="n/a",
                confidence=0.0,
                thinking_log=[],
            )

            return AnalysisReport(
                geotech_result=empty_result,
                contract_result=empty_result,
                orchestrator_result=empty_result,
                overall_risk_level="n/a",
                overall_confidence=0.0,
                executive_summary=(
                    f"## Documento No Relacionado\n\n"
                    f"**Tipo detectado:** {doc_type}\n\n"
                    f"**Motivo:** {reason}\n\n"
                    f"TerraTunnel Analyzer está diseñado exclusivamente para analizar "
                    f"especificaciones técnicas y contratos de construcción de túneles y "
                    f"obras subterráneas. El documento proporcionado no corresponde a "
                    f"este ámbito.\n\n"
                    f"**Tipos de documentos aceptados:**\n"
                    f"- Especificaciones técnicas de túneles (roca o suelo)\n"
                    f"- Informes Geotécnicos de Base (GBR)\n"
                    f"- Contratos de construcción subterránea (FIDIC, NEC, etc.)\n"
                    f"- Clasificaciones de roca (RMR, Q-system, GSI)\n"
                    f"- Diseños de sostenimiento de túneles"
                ),
                all_findings=[{
                    "id": "VAL-001",
                    "type": "validation",
                    "severity": "info",
                    "title": "Documento no relacionado con construcción de túneles",
                    "description": f"{doc_type}: {reason}",
                }],
                thinking_log=self.thinking_log,
            )

        except Exception as exc:
            # If validation fails, proceed with analysis anyway
            self._log("Orchestrator", f"Validation skipped (error: {exc})")
            return None

    # ------------------------------------------------------------------
    # Demo synthesis
    # ------------------------------------------------------------------

    def _demo_synthesis(
        self,
        geotech: AgentResult,
        contract: AgentResult,
    ) -> AgentResult:
        """Generate realistic demo orchestrator output."""
        data = {
            "cross_domain_findings": [
                {
                    "id": "XD-001",
                    "title": "Soporte insuficiente + Riesgo geológico transferido al contratista",
                    "geotech_finding_id": "GEO-001",
                    "contract_finding_id": "CTR-001",
                    "description": (
                        "CONFLICTO CRÍTICO: El agente geotécnico identifica que el sostenimiento "
                        "especificado para Clase IV es insuficiente (GEO-001), mientras que "
                        "simultáneamente el contrato transfiere todo el riesgo geológico al "
                        "contratista (CTR-001). Esto crea una trampa contractual: el contratista "
                        "debe ejecutar un sostenimiento inadecuado según contrato, pero será "
                        "responsable de cualquier colapso resultante. La combinación de "
                        "especificación técnica deficiente + transferencia total de riesgo es "
                        "la causa principal de disputas en proyectos de túneles."
                    ),
                    "combined_severity": "critical",
                    "recommended_action": (
                        "1) Corregir el diseño de sostenimiento para Clase IV según estándares "
                        "RMR/NATM. 2) Implementar cláusula de riesgo compartido basada en GBR "
                        "del FIDIC Emerald Book. 3) Establecer mecanismo de variación "
                        "automática cuando la clase de roca cambie."
                    ),
                },
                {
                    "id": "XD-002",
                    "title": "Ingreso de agua sin protocolo de pre-inyección + Ausencia de DSC",
                    "geotech_finding_id": "GEO-002",
                    "contract_finding_id": "CTR-003",
                    "description": (
                        "CONFLICTO ALTO: Se identifica riesgo de ingreso de agua a 5 bar "
                        "sin medidas de pre-inyección (GEO-002), y el contrato carece de "
                        "cláusula de Condiciones Diferentes del Sitio (CTR-003). Si se "
                        "encuentra agua a presión mayor que la prevista, el contratista no "
                        "tiene base contractual para reclamar los costos de tratamiento "
                        "adicional (grouting, congelamiento, etc.)."
                    ),
                    "combined_severity": "high",
                    "recommended_action": (
                        "1) Incorporar protocolo de pre-inyección en especificaciones. "
                        "2) Agregar cláusula DSC con línea base de ingreso de agua máximo "
                        "en L/min/10m de túnel. 3) Crear ítem de pago separado para "
                        "tratamiento de agua subterránea."
                    ),
                },
                {
                    "id": "XD-003",
                    "title": "Discrepancia RMR/Q en GBR + GBR sin líneas base cuantificadas",
                    "geotech_finding_id": "GEO-003",
                    "contract_finding_id": "CTR-002",
                    "description": (
                        "CONFLICTO ALTO: Existe una discrepancia técnica entre los valores "
                        "Q y RMR del GBR (GEO-003), y además el GBR no tiene líneas base "
                        "cuantificadas (CTR-002). Esto hace que el GBR sea virtualmente "
                        "inutilizable como herramienta de asignación de riesgo contractual."
                    ),
                    "combined_severity": "high",
                    "recommended_action": (
                        "Revisión completa del GBR: 1) Resolver discrepancias RMR/Q, "
                        "2) Establecer líneas base numéricas por tramo, 3) Incluir "
                        "distribución probabilística de clases de roca."
                    ),
                },
            ],
            "overall_risk_level": "critical",
            "overall_confidence": 0.90,
            "executive_summary": (
                "## Resumen Ejecutivo — Análisis Multi-Agente TerraTunnel\n\n"
                "El análisis integrado de las especificaciones técnicas y contractuales "
                "revela un **nivel de riesgo CRÍTICO** para este proyecto de túnel. "
                "Se identificaron **12 hallazgos** en total (6 geotécnicos, 6 contractuales) "
                "y **3 conflictos inter-disciplinarios** donde las deficiencias técnicas "
                "y contractuales se amplifican mutuamente.\n\n"
                "### Hallazgo Principal\n"
                "La combinación más peligrosa identificada es la coexistencia de un "
                "sostenimiento técnicamente insuficiente para las condiciones geológicas "
                "esperadas (Clase IV-V) con una transferencia total del riesgo geológico "
                "al contratista y un GBR que carece de líneas base cuantificables. "
                "Esta 'tormenta perfecta' contractual es la causa raíz de las disputas "
                "más costosas en la industria del túnel a nivel mundial.\n\n"
                "### Recomendaciones Prioritarias\n"
                "1. **Urgente**: Revisar y corregir el diseño de sostenimiento para Clases IV-V.\n"
                "2. **Urgente**: Reformular la cláusula 4.12 hacia un modelo de riesgo compartido "
                "basado en FIDIC Emerald Book.\n"
                "3. **Alta Prioridad**: Cuantificar todas las líneas base del GBR con "
                "parámetros medibles.\n"
                "4. **Alta Prioridad**: Incorporar cláusula DSC y protocolo de pre-inyección.\n"
                "5. **Media Prioridad**: Extender plazos de notificación y establecer DAB permanente."
            ),
            "risk_matrix": [
                {"risk_id": "GEO-001", "description": "Soporte insuficiente Clase IV", "likelihood": 4, "consequence": 5, "category": "geotechnical"},
                {"risk_id": "GEO-002", "description": "Ingreso de agua sin pre-inyección", "likelihood": 3, "consequence": 5, "category": "geotechnical"},
                {"risk_id": "GEO-003", "description": "Discrepancia RMR/Q en GBR", "likelihood": 5, "consequence": 3, "category": "geotechnical"},
                {"risk_id": "GEO-004", "description": "Roca expansiva no evaluada", "likelihood": 3, "consequence": 4, "category": "geotechnical"},
                {"risk_id": "GEO-005", "description": "Monitoreo insuficiente", "likelihood": 4, "consequence": 3, "category": "geotechnical"},
                {"risk_id": "CTR-001", "description": "Transferencia total riesgo geológico", "likelihood": 5, "consequence": 5, "category": "contractual"},
                {"risk_id": "CTR-002", "description": "GBR sin líneas base cuantificables", "likelihood": 5, "consequence": 4, "category": "contractual"},
                {"risk_id": "CTR-003", "description": "Ausencia de cláusula DSC", "likelihood": 5, "consequence": 4, "category": "contractual"},
                {"risk_id": "CTR-004", "description": "Plazo notificación 7 días", "likelihood": 4, "consequence": 3, "category": "contractual"},
                {"risk_id": "CTR-005", "description": "Sin DAB permanente", "likelihood": 3, "consequence": 3, "category": "contractual"},
                {"risk_id": "CTR-006", "description": "Pago global sin variabilidad", "likelihood": 4, "consequence": 4, "category": "contractual"},
                {"risk_id": "XD-001", "description": "Soporte insuficiente + riesgo transferido", "likelihood": 4, "consequence": 5, "category": "cross-domain"},
                {"risk_id": "XD-002", "description": "Agua sin protocolo + sin DSC", "likelihood": 3, "consequence": 5, "category": "cross-domain"},
                {"risk_id": "XD-003", "description": "GBR inconsistente + no cuantificado", "likelihood": 5, "consequence": 4, "category": "cross-domain"},
            ],
            "support_comparison": [
                {
                    "section": "Tramo 1 (Km 0+000 – 1+500)",
                    "rock_class": "Clase II–III (RMR 55-70)",
                    "contract_support": "Tipo I: Pernos puntuales 3m, shotcrete 50mm puntual",
                    "standard_support": "Pernos puntuales 3m, shotcrete 50mm donde necesario (Bieniawski Tabla 6.6)",
                    "status": "ok",
                    "recommendation": "Conforme. El sostenimiento es adecuado para las condiciones descritas.",
                },
                {
                    "section": "Tramo 2 (Km 1+500 – 2+400)",
                    "rock_class": "Clase III–IV (Q=0.4 ≠ RMR 41-60)",
                    "contract_support": "Tipo II: Pernos sistemáticos 3m @ 2.0m",
                    "standard_support": "Pernos 4m @ 1.5m + shotcrete 100mm + malla electrosoldada (para Q=0.4, RMR ≈ 28)",
                    "status": "warning",
                    "recommendation": "Discrepancia RMR/Q. Si Q=0.4 es correcto, el sostenimiento es insuficiente. Aumentar a Tipo III con shotcrete reforzado.",
                },
                {
                    "section": "Tramo 3 (Km 2+400 – 3+100)",
                    "rock_class": "Clase IV (RMR 30-35)",
                    "contract_support": "Tipo III: Pernos puntuales sin shotcrete",
                    "standard_support": "Pernos SN 4-5m @ 1.0-1.5m + shotcrete 100-150mm fibra acero + cerchas HEB @ 1.5m (Bieniawski 1989)",
                    "status": "critical",
                    "recommendation": "INSUFICIENTE. Clase IV requiere sostenimiento pesado. Agregar: shotcrete 150mm fibra acero, pernos 4m @ 1.2x1.2m, cerchas HEB-100 @ 1.5m. Incluir pre-inyección por presión de agua 5 bar.",
                },
                {
                    "section": "Tramo 4 (Km 3+100 – 4+200)",
                    "rock_class": "Clase II (RMR 60-75)",
                    "contract_support": "Tipo I: Pernos puntuales 3m, shotcrete 50mm puntual",
                    "standard_support": "Pernos puntuales o sistemáticos 3m, shotcrete 50mm puntual (Bieniawski Tabla 6.6)",
                    "status": "ok",
                    "recommendation": "Conforme. Verificar transición Tramo 3→4 con sostenimiento transitorio.",
                },
            ],
        }

        raw = json.dumps(data, ensure_ascii=False, indent=2)
        from .core import AgentMessage as AM
        self.director.history.append(AM(role="assistant", content=raw))

        return AgentResult(
            agent_name="Tunnel-Director",
            raw_response=raw,
            findings=data["cross_domain_findings"],
            risk_level=data["overall_risk_level"],
            confidence=data["overall_confidence"],
            thinking_log=[
                "[Tunnel-Director] Running in DEMO mode",
                "[Tunnel-Director] Cross-referencing 6 geotech + 6 contract findings",
                "[Tunnel-Director] Identified 3 cross-domain conflicts",
                "[Tunnel-Director] Generated unified risk matrix (14 entries)",
                "[Tunnel-Director] Synthesis complete",
            ],
        )
