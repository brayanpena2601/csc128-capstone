"""Extract allowlisted topics and resource types, including short slot answers."""
import re

TOPICS = {
    "capstone": ("capstone", "final project", "proyecto final"),
    "slot filling": ("slot filling", "entities", "entity", "entidades"),
    "intents": ("intents", "intent", "intent classification", "intenciones"),
    "conversation state": ("conversation state", "conversation memory", "state", "estado"),
    "grounding": ("grounding", "retrieval", "retriever"),
    "streamlit": ("streamlit", "deployment", "deploy", "despliegue"),
    "groq": ("groq", "api", "rate limit"),
}
RESOURCE_TYPES = {
    "notes": ("notes", "lesson", "notas"),
    "instructions": ("instructions", "requirements", "instrucciones", "requisitos"),
    "examples": ("example", "examples", "ejemplo", "ejemplos"),
}


def candidates(text: str) -> dict[str, list[str]]:
    text = text.lower()
    matches = {"topic": [], "resource_type": []}
    for name, choices in (("topic", TOPICS), ("resource_type", RESOURCE_TYPES)):
        for value, aliases in choices.items():
            if any(re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text) for alias in aliases):
                matches[name].append(value)
    return matches


def extract(text: str) -> dict[str, str]:
    return {name: values[0] for name, values in candidates(text).items() if len(values) == 1}
