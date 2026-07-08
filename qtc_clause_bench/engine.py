"""Prompt building, the model call, and schema validation.

`_call_model` is the only function that talks to a model provider. Swap
providers by replacing it and keeping the (prompt, model, temperature) -> str
contract.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import jsonschema

from qtc_clause_bench.clauses import CLAUSE_DESCRIPTIONS

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
SCHEMA_DIR = ROOT / "schema"

DEFAULT_MODEL = os.environ.get("QTC_BENCH_MODEL", "claude-sonnet-4-5")


class SchemaError(RuntimeError):
    """Raised when a model output fails JSON Schema validation."""


def _read_schema() -> dict:
    return json.loads((SCHEMA_DIR / "extraction_result.schema.json").read_text(encoding="utf-8"))


def _render(template: str, **slots: str) -> str:
    out = template
    for key, value in slots.items():
        out = out.replace("{" + key + "}", value)
    return out


def build_clause_descriptions_block() -> str:
    lines = [f"- **{key}**: {desc}" for key, desc in CLAUSE_DESCRIPTIONS.items()]
    return "\n".join(lines)


def build_extraction_prompt(contract_text: str) -> str:
    template = (PROMPTS_DIR / "clause_extraction.prompt.md").read_text(encoding="utf-8")
    schema = _read_schema()
    return _render(
        template,
        clause_descriptions=build_clause_descriptions_block(),
        contract_text=contract_text,
        output_schema=json.dumps(schema, indent=2),
    )


def _call_model(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.2) -> str:
    """The one function that talks to a model provider. Requires ANTHROPIC_API_KEY."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(json)?", "", raw).rstrip("`").strip()
    return json.loads(raw)


def extract(contract_id: str, contract_text: str, model: str = DEFAULT_MODEL) -> dict:
    """Run extraction end to end for one contract: prompt, model call, schema check."""
    prompt = build_extraction_prompt(contract_text)
    raw = _call_model(prompt, model=model)
    result = _parse_json_response(raw)
    result.setdefault("contract_id", contract_id)

    schema = _read_schema()
    try:
        jsonschema.validate(result, schema)
    except jsonschema.ValidationError as e:
        raise SchemaError(f"contract={contract_id}: {e.message}") from e

    return result
