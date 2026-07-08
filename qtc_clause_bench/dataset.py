"""Loads the synthetic contract/annotation pairs that make up the benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT / "data" / "contracts"
ANNOTATIONS_DIR = ROOT / "data" / "annotations"


@dataclass(frozen=True)
class Example:
    contract_id: str
    text: str
    annotation: dict


def list_contract_ids() -> list[str]:
    """Return every contract_id that has both a contract file and an annotation file."""
    contract_stems = {p.stem for p in CONTRACTS_DIR.glob("*.txt")}
    annotation_stems = {p.stem for p in ANNOTATIONS_DIR.glob("*.json")}
    missing_annotations = contract_stems - annotation_stems
    missing_contracts = annotation_stems - contract_stems
    if missing_annotations:
        raise FileNotFoundError(f"contracts with no annotation file: {sorted(missing_annotations)}")
    if missing_contracts:
        raise FileNotFoundError(f"annotations with no contract file: {sorted(missing_contracts)}")
    return sorted(contract_stems)


def load_contract_text(contract_id: str) -> str:
    path = CONTRACTS_DIR / f"{contract_id}.txt"
    return path.read_text(encoding="utf-8")


def load_annotation(contract_id: str) -> dict:
    path = ANNOTATIONS_DIR / f"{contract_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_dataset() -> list[Example]:
    return [
        Example(contract_id=cid, text=load_contract_text(cid), annotation=load_annotation(cid))
        for cid in list_contract_ids()
    ]
