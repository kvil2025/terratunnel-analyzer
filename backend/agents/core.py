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
        self.thinking_log.append(f"[{self.name}] Calling {self._model} …")
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[m.to_api() for m in self.history],
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            self.history.append(AgentMessage(role="assistant", content=content))
            self.thinking_log.append(f"[{self.name}] Received response ({len(content)} chars)")
            return self._parse_response(content)

        except Exception as exc:
            error_msg = f"[{self.name}] API error: {exc}"
            self.thinking_log.append(error_msg)
            return AgentResult(
                agent_name=self.name,
                raw_response=error_msg,
                findings=[{"type": "error", "description": str(exc)}],
                risk_level="unknown",
                confidence=0.0,
                thinking_log=list(self.thinking_log),
            )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(self, content: str) -> AgentResult:
        """Try to parse the assistant response as JSON; fall back to plain text."""
        try:
            data = json.loads(content)
            return AgentResult(
                agent_name=self.name,
                raw_response=content,
                findings=data.get("findings", []),
                risk_level=data.get("risk_level", "medium"),
                confidence=data.get("confidence", 0.75),
                thinking_log=list(self.thinking_log),
            )
        except json.JSONDecodeError:
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
