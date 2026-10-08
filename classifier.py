"""Small, inspectable rule classifier; unknown input never defaults to an intent."""
import re

INTENTS = ("resource_lookup", "concept_help", "assignment_guidance", "course_logistics")


def classify(text: str) -> str | None:
    text = text.lower()
    rules = (
        ("course_logistics", r"\b(due|deadline|when|office hours|contact|points|fecha|cuando|cuándo)\b"),
        ("resource_lookup", r"\b(find|resource|resources|notes|examples|link|where|buscar|recursos|notas|ejemplos)\b"),
        ("assignment_guidance", r"\b(requirements|instructions|deliverables|submit|turn in|need to do|rubric|assignment|checklist|requisitos|entregar|instrucciones)\b"),
        ("concept_help", r"\b(explain|concept|understand|what is|what are|explica|qué es|que es)\b"),
    )
    for intent, pattern in rules:
        if re.search(pattern, text):
            return intent
    return None
