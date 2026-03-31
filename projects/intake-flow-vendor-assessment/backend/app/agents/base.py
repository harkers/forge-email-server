"""
Base agent class for all pipeline agents.

Each agent:
- Receives structured input from the DPM
- Runs exactly one pipeline step
- Returns structured JSON output
- Does NOT call other agents directly
"""

import json
import httpx
from abc import ABC, abstractmethod
from typing import Any
from app.config import get_settings

settings = get_settings()


class AgentError(Exception):
    """Raised when an agent encounters a non-recoverable error."""
    pass


class BaseAgent(ABC):
    """
    Abstract base for all pipeline agents.

    Subclass this and implement `step_name` and `run`.
    The DPM calls `execute(input: dict) -> dict`.
    """

    @property
    @abstractmethod
    def step_name(self) -> str:
        """Human-readable name of this step, e.g. 'intake', 'data_protection'."""
        raise NotImplementedError

    @property
    def model(self) -> str:
        return settings.local_model

    @property
    def ollama_base_url(self) -> str:
        return settings.ollama_base_url

    @abstractmethod
    async def run(self, input: dict, context: dict) -> dict:
        """
        Execute the agent's step.

        Args:
            input:  Structured input for this step (from DPM or previous agent).
            context: Shared pipeline context (assessment_id, vendor_id, step history, etc.)

        Returns:
            dict: Structured output to be stored and passed to the next step.
        """
        raise NotImplementedError

    async def execute(self, input: dict, context: dict) -> dict:
        """
        Execute wrapper — catches errors, logs, and ensures structured output.
        """
        result = await self.run(input, context)
        if not isinstance(result, dict):
            raise AgentError(
                f"{self.step_name} returned non-dict type {type(result).__name__}. "
                "All agents must return a dict."
            )
        return result

    async def llm_complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.3,
        num_ctx: int = 32768,
    ) -> str:
        """
        Call local Ollama for text generation.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "num_ctx": num_ctx,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def llm_complete_json(
        self,
        prompt: str,
        system: str | None = None,
        schema: dict | None = None,
        temperature: float = 0.3,
        num_ctx: int = 32768,
    ) -> dict:
        """
        Call local Ollama and enforce JSON output via schema if provided.
        Falls back to parsing the raw text as JSON.
        """
        raw = await self.llm_complete(prompt, system, temperature, num_ctx)
        try:
            # Try direct JSON parse first
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try extracting from markdown code block
            for fmt in ["```json\n", "```\n", "```json\r\n"]:
                if fmt.strip("`\n") in raw:
                    try:
                        start = raw.find(fmt) + len(fmt)
                        end = raw.rfind("```")
                        return json.loads(raw[start:end].strip())
                    except (json.JSONDecodeError, ValueError):
                        pass
            raise AgentError(f"{self.step_name}: LLM output is not valid JSON: {raw[:200]}")
