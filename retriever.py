"""Exact metadata retrieval avoids inventing unavailable course resources."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "resources.json"


def retrieve(intent: str, slots: dict[str, str]) -> list[dict]:
    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return [record for record in records
            if intent in record["intents"]
            and record["topic"] == slots.get("topic")
            and (intent != "resource_lookup" or record["resource_type"] == slots.get("resource_type"))]
