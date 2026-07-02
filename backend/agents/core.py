"""
TerraTunnel Analyzer — Agent Core Engine
=========================================
Provides the base `Agent` class that wraps GLM-5.2 (or any OpenAI-compatible
endpoint) with streaming, retry logic, and a structured output contract.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _get_client() -> OpenAI:
    """Return a configured OpenAI client pointing at the Z.ai endpoint."""
    return OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY", "demo-key"),
        base_url=os.getenv("ZHIPU_API_BASE", "https://api.z.ai/api/paas/v4"),
    )


def _model_id() -> str:
    return os.getenv("GLM_MODEL", "glm-5.2")


def is_demo_mode() -> bool:
    """Auto-detect mode: LIVE if a real API key is present, DEMO otherwise.
    The MODE env var can override: MODE=demo forces demo, MODE=live forces live.
    """
    explicit = os.getenv("MODE", "").lower()
    if explicit == "demo":
        return True
    if explicit == "live":
        return False
    # Auto-detect: check if API key looks real
    key = os.getenv("ZHIPU_API_KEY", "")
    return not key or key in ("", "your_api_key_here", "demo-key", "sk-xxx")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentMessage:
    """A single message in an agent's conversation."""
    role: str          # "system" | "user" | "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_api(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentResult:
    """Structured output from an agent run."""
    agent_name: str
    raw_response: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    risk_level: str = "medium"          # low | medium | high | critical
    confidence: float = 0.0
    thinking_log: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "raw_response": self.raw_response,
            "findings": self.findings,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "thinking_log": self.thinking_log,
        }


# ---------------------------------------------------------------------------
# Agent base class
# ---------------------------------------------------------------------------

class Agent:
    """
    An autonomous LLM-powered agent backed by GLM-5.2.

    Each agent has:
      - A *name* and *role description* (injected as the system prompt).
      - An internal message history.
      - A `run()` method that sends the conversation to the LLM and returns
        an `AgentResult` with parsed JSON findings.
    """

    def __init__(self, name: str, system_prompt: str) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.history: list[AgentMessage] = [
            AgentMessage(role="system", content=system_prompt),
        ]
        self._client = _get_client()
        self._model = _model_id()
        self.thinking_log: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, user_input: str) -> AgentResult:
        """Execute the agent on *user_input* and return structured results."""
        self.thinking_log.append(f"[{self.name}] Received input ({len(user_input)} chars)")
        self.history.append(AgentMessage(role="user", content=user_input))

        if is_demo_mode():
            return self._demo_run(user_input)

        return self._live_run()

    # ------------------------------------------------------------------
    # Live LLM call
    # ------------------------------------------------------------------

    def _live_run(self) -> AgentResult:
        import time as _time

        self.thinking_log.append(f"[{self.name}] Calling {self._model} …")

        max_retries = 3
        retry_delays = [2, 5, 10]  # seconds

        for attempt in range(max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[m.to_api() for m in self.history],
                    temperature=0.3,
                    max_tokens=4096,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or ""
                self.history.append(AgentMessage(role="assistant", content=content))
                self.thinking_log.append(f"[{self.name}] Received response ({len(content)} chars)")
                return self._parse_response(content)

            except Exception as exc:
                error_str = str(exc)

                # Retry on rate limit (429)
                if "429" in error_str and attempt < max_retries:
                    delay = retry_delays[attempt]
                    self.thinking_log.append(
                        f"[{self.name}] Rate limit (429). Retry {attempt + 1}/{max_retries} in {delay}s …"
                    )
                    _time.sleep(delay)
                    continue

                # Non-retryable error or max retries exhausted
                if "429" in error_str:
                    user_msg = (
                        f"Límite de cuota de Gemini excedido. "
                        f"El plan gratuito permite ~20 solicitudes/día para gemini-2.5-flash. "
                        f"Opciones: (1) Esperar unos minutos y reintentar, "
                        f"(2) Usar otro API key, (3) Actualizar a plan de pago en ai.google.dev"
                    )
                else:
                    user_msg = f"Error de API: {error_str[:200]}"

                self.thinking_log.append(f"[{self.name}] API error: {error_str[:200]}")
                return AgentResult(
                    agent_name=self.name,
                    raw_response=error_str,
                    findings=[{
                        "id": "ERR-001",
                        "type": "error",
                        "severity": "critical",
                        "title": "Error de API",
                        "description": user_msg,
                        "recommended_action": "Reintentar el análisis o verificar la configuración del API key.",
                    }],
                    risk_level="unknown",
                    confidence=0.0,
                    thinking_log=list(self.thinking_log),
                )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(self, content: str) -> AgentResult:
        """Try to parse the assistant response as JSON; fall back to plain text."""
        import re

        def _try_parse(text: str) -> dict | None:
            """Attempt to parse a string as JSON."""
            text = text.strip()
            if not text:
                return None
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None

        # Strategy 1: Direct parse
        data = _try_parse(content)

        # Strategy 2: Extract from markdown code fence ```json ... ```
        if data is None:
            md_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', content, re.DOTALL)
            if md_match:
                data = _try_parse(md_match.group(1))

        # Strategy 3: Find the first { ... } block (greedy)
        if data is None:
            brace_match = re.search(r'\{.*\}', content, re.DOTALL)
            if brace_match:
                data = _try_parse(brace_match.group(0))

        if data is not None and isinstance(data, dict):
            findings = data.get("findings", [])
            self.thinking_log.append(
                f"[{self.name}] Parsed JSON: {len(findings)} findings"
            )
            return AgentResult(
                agent_name=self.name,
                raw_response=content,
                findings=findings,
                risk_level=data.get("risk_level", "medium"),
                confidence=data.get("confidence", 0.75),
                thinking_log=list(self.thinking_log),
            )

        # All strategies failed — wrap as text
        self.thinking_log.append(f"[{self.name}] Response was not valid JSON, wrapping as text.")
        return AgentResult(
            agent_name=self.name,
            raw_response=content,
            findings=[{"type": "text", "description": content}],
            risk_level="medium",
            confidence=0.5,
            thinking_log=list(self.thinking_log),
        )

    # ------------------------------------------------------------------
    # Demo mode (no API key required)
    # ------------------------------------------------------------------

    def _demo_run(self, user_input: str) -> AgentResult:
        """Return realistic mock data so the UI can be fully tested."""
        self.thinking_log.append(f"[{self.name}] Running in DEMO mode")
        # Sub-classes override _demo_findings() to return domain-specific data
        findings, risk_level, confidence = self._demo_findings(user_input)
        raw = json.dumps({
            "findings": findings,
            "risk_level": risk_level,
            "confidence": confidence,
        }, ensure_ascii=False, indent=2)
        self.history.append(AgentMessage(role="assistant", content=raw))
        return AgentResult(
            agent_name=self.name,
            raw_response=raw,
            findings=findings,
            risk_level=risk_level,
            confidence=confidence,
            thinking_log=list(self.thinking_log),
        )

    def _demo_findings(
        self, user_input: str
    ) -> tuple[list[dict[str, Any]], str, float]:
        """Override in subclasses for domain-specific demo data."""
        return (
            [{"type": "info", "description": "Demo finding from base agent."}],
            "medium",
            0.5,
        )
