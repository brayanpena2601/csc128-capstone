"""Exact metadata retrieval avoids inventing unavailable course resources."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "resources.json"


class SourceError(Exception):
    """Source storage is unavailable or invalid; callers must not invent facts."""


def retrieve(intent: str, slots: dict[str, str]) -> list[dict]:
    try:
        records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("Expected records")
        for record in records:
            if not isinstance(record, dict) or not all(
                isinstance(record.get(key), str) and record[key].strip()
                for key in ("id", "topic", "resource_type", "source", "text")
            ) or not isinstance(record.get("intents"), list) or not all(
                isinstance(value, str) for value in record["intents"]
            ):
                raise ValueError("Invalid source record")
    except (OSError, ValueError, UnicodeError) as error:
        raise SourceError("Course sources unavailable") from error
    return [record for record in records
            if intent in record["intents"]
            and record["topic"] == slots.get("topic")
            and (intent != "resource_lookup" or record["resource_type"] == slots.get("resource_type"))]
